"""Inspect a trained sklearn/joblib pipeline.

Usage:  python scripts/inspect_model.py [path/to/model.joblib]

Prints the features the model expects (feature_names_in_), encoder categories
and the estimator type — use this to verify compatibility with the API's
canonical inputs after dropping your model into ml/model.joblib.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

import joblib  # noqa: E402
from django.conf import settings  # noqa: E402


def walk(obj, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if depth > 8 or id(obj) in seen:
        return
    seen.add(id(obj))
    print("  " * depth + f"- {type(obj).__module__}.{type(obj).__name__}")
    names = getattr(obj, "feature_names_in_", None)
    if names is not None:
        print("  " * (depth + 1) + f"expects features: {list(names)}")
    for attr in ("n_features_in_", "classes_", "feature_importances_"):
        value = getattr(obj, attr, None)
        if value is not None and attr != "feature_importances_":
            print("  " * (depth + 1) + f"{attr}: {value}")
    steps = getattr(obj, "steps", None)
    if steps:
        for _, step in steps:
            walk(step, depth + 1, seen)
    transformers = getattr(obj, "transformers_", None)
    if transformers:
        for entry in transformers:
            if isinstance(entry, (list, tuple)) and entry:
                transformer = entry[-1]
                if transformer not in ("drop", "passthrough"):
                    walk(transformer, depth + 1, seen)


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else settings.ML_MODEL_PATH)
    if not path.exists() and path.suffix != ".pkl":
        alt = path.with_suffix(".pkl")
        if alt.exists():
            path = alt
    print(f"Inspecting: {path}")
    if not os.path.exists(path):
        print("!! File not found. Copy your trained .joblib/.pkl to this path first.")
        sys.exit(1)
    model = joblib.load(path)
    walk(model)
    names = getattr(model, "feature_names_in_", None)
    if names is not None and hasattr(model, "steps") and not hasattr(model, "predict"):
        estimator = model.steps[-1][1]
        inner = getattr(estimator, "feature_names_in_", None)
        if inner is not None:
            print(f"Final estimator expects: {list(inner)}")
    print("\nIf the expected names differ from the API's canonical inputs")
    print("(locality, total_sqft, bhk, bathrooms, furnishing, property_age,")
    print("parking, clubhouse, metro_distance_km), set ML_FEATURE_ALIASES in .env:")
    print('  ML_FEATURE_ALIASES={"total_sqft": "size", "bhk": "bedrooms"}')


if __name__ == "__main__":
    main()
