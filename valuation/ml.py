"""In-memory ML pipeline for house-price prediction.

Loads the XGBoost (sklearn Pipeline) from ``ML_MODEL_PATH`` once at startup
and serves predictions. The loader is *adaptive*:

* If the fitted pipeline exposes ``feature_names_in_`` (the sklearn standard,
  shared by ColumnTransformer pipelines), the input DataFrame is built with
  exactly those columns, resolved through a configurable alias map
  (``ML_FEATURE_ALIASES`` env var, JSON: ``{"total_sqft": "size"}``).
* If the model file is missing, a deterministic heuristic estimator keeps the
  whole product usable for development — clearly flagged as ``fallback``.

Accepted formats: ``.joblib`` (recommended) or ``.pkl`` — either name works at
the configured path; the loader auto-detects a sibling ``.pkl``/``.joblib``.

Use ``scripts/inspect_model.py`` to print what your model expects.
"""

import json
import logging
import threading
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from django.conf import settings

logger = logging.getLogger(__name__)

# Canonical feature names used across the API/frontend.
CANONICAL_FEATURES = [
    "locality",
    "total_sqft",
    "bhk",
    "bathrooms",
    "furnishing",
    "property_age",
    "parking",
    "clubhouse",
    "metro_distance_km",
]

# Common column-name variants seen in housing datasets (Kaggle et al.).
DEFAULT_ALIASES: Dict[str, List[str]] = {
    "locality": ["locality", "location", "area", "site_location", "neighborhood", "neighbourhood"],
    "total_sqft": ["total_sqft", "sqft", "size", "area_sqft", "total_sqft_ft2", "area_in_sqft"],
    "bhk": ["bhk", "bedrooms", "beds", "no_of_bedrooms", "size_in_bhk"],
    "bathrooms": ["bathrooms", "bath", "baths", "no_of_bathrooms"],
    "furnishing": ["furnishing", "furnishing_status", "furnished"],
    "property_age": ["property_age", "age", "age_years", "age_of_property"],
    "parking": ["parking", "has_parking", "car_parking"],
    "clubhouse": ["clubhouse", "has_clubhouse", "club_house", "gym"],
    "metro_distance_km": ["metro_distance_km", "metro_distance", "distance_to_metro", "metro"],
}

FURNISHING_LABELS = {
    "unfurnished": "Unfurnished",
    "semi_furnished": "Semi-Furnished",
    "fully_furnished": "Fully-Furnished",
}

DEFAULT_LOCALITIES = [
    "Whitefield", "Indiranagar", "Koramangala", "HSR Layout", "Electronic City",
    "Hebbal", "Jayanagar", "J P Nagar", "Marathahalli", "Sarjapur Road",
    "Bellandur", "Yelahanka", "Rajajinagar", "Malleshwaram", "Banashankari",
    "Powai", "Andheri West", "Thane West", "Sector 62 Noida", "Gurgaon Sohna Road",
]

# Fallback heuristic baselines (₹/sqft multipliers) — demo only.
_LOCALITY_MULTIPLIERS = {
    "indiranagar": 1.9, "koramangala": 1.8, "hsr layout": 1.6,
    "sarjapur road": 1.4, "whitefield": 1.1, "marathahalli": 1.15,
    "electronic city": 0.9, "hebbal": 1.3, "jayanagar": 1.5,
    "j p nagar": 1.3, "bellandur": 1.35, "yelahanka": 1.0,
    "rajajinagar": 1.35, "malleshwaram": 1.7, "banashankari": 1.25,
    "powai": 2.0, "andheri west": 2.2, "thane west": 1.4,
    "sector 62 noida": 1.2, "gurgaon sohna road": 1.5,
}
_BASE_PER_SQFT = 6500.0


def _parse_env_json(raw: str, expect: type):
    if not raw:
        return None
    try:
        value = json.loads(raw)
        if not isinstance(value, expect):
            return None
        return value
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in env var — ignoring. Value: %r", raw)
        return None


class PriceModel:
    """Thread-safe, lazy, in-memory singleton around the joblib pipeline."""

    def __init__(self) -> None:
        self._model = None
        self._loaded = False
        self._lock = threading.Lock()

    # -- loading ------------------------------------------------------------

    @property
    def pipeline(self):
        self.load()
        return self._model

    @property
    def is_fitted(self) -> bool:
        self.load()
        return self._model is not None

    def load(self):
        if self._loaded:
            return self._model
        with self._lock:
            if self._loaded:
                return self._model
            path = settings.ML_MODEL_PATH
            if not path.exists():
                # Convenience: a .pkl sitting next to the configured path is
                # accepted too (e.g. ML_MODEL_PATH=ml/model.joblib picks up
                # ml/model.pkl automatically, and vice-versa).
                alt = path.with_suffix(".pkl")
                if alt.exists():
                    path = alt
            if path.exists():
                try:
                    self._model = self._load_any(path)
                    logger.info("Loaded ML pipeline from %s", path)
                except Exception:
                    logger.exception("Failed to load ML pipeline from %s", path)
                    self._model = None
            else:
                logger.warning(
                    "ML model not found at %s (or %s) — using the heuristic "
                    "fallback estimator. Drop your trained .joblib/.pkl there "
                    "to enable real XGBoost predictions.",
                    settings.ML_MODEL_PATH,
                    settings.ML_MODEL_PATH.with_suffix(".pkl"),
                )
            self._loaded = True
            return self._model

    @staticmethod
    def _load_any(path):
        """joblib handles .joblib and most .pkl files; fall back to raw pickle."""
        try:
            return joblib.load(path)
        except Exception:
            import pickle

            with open(path, "rb") as fh:
                return pickle.load(fh)

    # -- feature engineering --------------------------------------------------

    def _aliases(self) -> Dict[str, List[str]]:
        custom = _parse_env_json(settings.ML_FEATURE_ALIASES, dict) or {}
        merged = {key: list(values) for key, values in DEFAULT_ALIASES.items()}
        for canonical, column in custom.items():
            merged.setdefault(canonical, [])
            merged[canonical] = [column] + [c for c in merged[canonical] if c != column]
        return merged

    def _build_dataframe(self, payload: Dict[str, Any]) -> pd.DataFrame:
        model = self.pipeline
        aliases = self._aliases()
        row: Dict[str, Any] = {}

        def value_for(canonical: str) -> Any:
            value = payload.get(canonical)
            if value is None:
                return None
            if canonical == "furnishing":
                return FURNISHING_LABELS.get(value, value)
            if isinstance(value, bool):
                return int(value)
            return value

        expected = getattr(model, "feature_names_in_", None)
        if expected is None and hasattr(model, "steps"):
            expected = getattr(model.steps[-1][1], "feature_names_in_", None)

        if expected is not None:
            expected = [str(name) for name in expected]
            for column in expected:
                if column in row:
                    continue
                matched = False
                for canonical, names in aliases.items():
                    if column in names:
                        value = value_for(canonical)
                        if value is not None:
                            row[column] = value
                            matched = True
                        break
                if not matched:
                    raise ValueError(
                        f"Model requires feature '{column}' which the API does not "
                        f"supply. Map it via ML_FEATURE_ALIASES env var "
                        f"(JSON, e.g. {{\"total_sqft\": \"{column}\"}}) or retrain."
                    )
            return pd.DataFrame([row], columns=expected)

        # No feature metadata — pass canonical columns directly.
        for canonical in CANONICAL_FEATURES:
            value = value_for(canonical)
            if value is not None:
                row[canonical] = value
        return pd.DataFrame([row])

    # -- localities -----------------------------------------------------------

    def localities(self) -> List[str]:
        found: set = set()
        env_localities = _parse_env_json(settings.ML_LOCALITIES, list)
        if env_localities:
            found.update(str(item) for item in env_localities)
        else:
            found.update(DEFAULT_LOCALITIES)
        if self.is_fitted:
            found.update(self._encoder_categories())
        return sorted(found)

    def _encoder_categories(self) -> set:
        found: set = set()
        seen: set = set()

        def walk(obj: Any, depth: int = 0) -> None:
            if depth > 6 or id(obj) in seen:
                return
            seen.add(id(obj))
            categories = getattr(obj, "categories_", None)
            if categories is not None:
                for arr in categories:
                    try:
                        found.update(str(c) for c in arr)
                    except TypeError:
                        continue
            steps = getattr(obj, "steps", None)
            if steps:
                for _, step in steps:
                    walk(step, depth + 1)
            transformers = getattr(obj, "transformers_", None)
            if transformers:
                for entry in transformers:
                    transformer = entry[-1] if isinstance(entry, (list, tuple)) and entry else None
                    if transformer is not None and transformer != "drop":
                        walk(transformer, depth + 1)

        try:
            walk(self.pipeline)
        except Exception:
            logger.debug("Encoder introspection failed", exc_info=True)
        return found

    # -- prediction -------------------------------------------------------------

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        locality = str(payload["locality"])
        sqft = float(payload["total_sqft"])

        if self.is_fitted:
            frame = self._build_dataframe(payload)
            try:
                price = float(self.pipeline.predict(frame)[0])
            except Exception as exc:
                raise RuntimeError(
                    f"Model inference failed: {exc}. Run "
                    f"`python scripts/inspect_model.py` to verify the expected features."
                ) from exc
            if price <= 0:
                raise RuntimeError(f"Model returned a non-positive price ({price}).")
            model_used = "xgboost"
        else:
            price = self._heuristic(payload)
            model_used = "fallback"

        low, high = price * 0.96, price * 1.04
        return {
            "estimated_price": round(price, 2),
            "price_per_sqft": round(price / sqft, 2),
            "range_low": round(low, 2),
            "range_high": round(high, 2),
            "model_used": model_used,
            "locality": locality,
        }

    def _heuristic(self, payload: Dict[str, Any]) -> float:
        """Deterministic demo estimator — only used when no model file exists."""
        multiplier = _LOCALITY_MULTIPLIERS.get(
            payload["locality"].strip().lower(), 1.0
        )
        per_sqft = _BASE_PER_SQFT * multiplier

        sqft = float(payload["total_sqft"])
        if sqft >= 2000:
            per_sqft *= 1.08
        elif sqft >= 1200:
            per_sqft *= 1.04

        furnishing = payload.get("furnishing", "unfurnished")
        per_sqft *= {"fully_furnished": 1.07, "semi_furnished": 1.03}.get(furnishing, 1.0)

        age = float(payload.get("property_age", 0) or 0)
        per_sqft *= max(0.80, 1.0 - 0.01 * age)

        if payload.get("parking"):
            per_sqft *= 1.02
        if payload.get("clubhouse"):
            per_sqft *= 1.02
        metro_km = payload.get("metro_distance_km")
        if metro_km is not None and float(metro_km) <= 1.0:
            per_sqft *= 1.04

        return per_sqft * sqft


price_model = PriceModel()
