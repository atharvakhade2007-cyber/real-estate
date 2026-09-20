"""
Django settings for myproject project — PropVal AI backend.

Single-server deployment: Django serves both the REST API and the built
React SPA (frontend/dist). Environment-driven configuration (12-factor).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the repo root (next to manage.py).
load_dotenv(BASE_DIR / ".env")


def env(key: str, default=None):
    return os.environ.get(key, default)


def env_bool(key: str, default: str = "False") -> bool:
    return env(key, default).strip().lower() in ("1", "true", "yes", "on")


def env_list(key: str, default: str = "") -> list:
    return [item.strip() for item in env(key, default).split(",") if item.strip()]


# --- Core -----------------------------------------------------------------

SECRET_KEY = env("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = env_bool("DJANGO_DEBUG", "True")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    # Local
    "valuation",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"


# --- Database (Supabase Postgres) -----------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", "postgres"),
        "USER": env("DB_USER", "postgres"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT", "5432"),
        "OPTIONS": {"sslmode": env("DB_SSLMODE", "require")},
        "CONN_MAX_AGE": 60,
    }
}


# --- Password validation / i18n --------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIMEZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True


# --- Static & media ---------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Where the Vite production build lands. Django serves this directory at "/"
# when DJANGO_SERVE_FRONTEND=True (single-server mode).
FRONTEND_DIST_DIR = Path(env("FRONTEND_DIST_DIR", str(BASE_DIR / "frontend" / "dist")))
SERVE_FRONTEND = env_bool("DJANGO_SERVE_FRONTEND", "True")

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / "media")))
REPORTS_DIR = MEDIA_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# --- DRF ---------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.ScopedRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"predict": "60/min", "reports": "20/min"},
}


# --- ML model ----------------------------------------------------------------

ML_MODEL_PATH = Path(
    env("ML_MODEL_PATH", str(BASE_DIR / "ml" / "model.joblib"))
)
# Optional JSON mapping of canonical feature -> column name expected by the
# model, e.g. {"total_sqft": "size", "bhk": "bedrooms"}.
ML_FEATURE_ALIASES = env("ML_FEATURE_ALIASES", "")
# Optional JSON list of locality strings the model was trained on.
ML_LOCALITIES = env("ML_LOCALITIES", "")


# --- Email --------------------------------------------------------------------

# Defaults to console backend until SMTP credentials are added to .env.
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", "")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", "True")
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", "False")
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "PropVal AI <noreply@propval.ai>")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
