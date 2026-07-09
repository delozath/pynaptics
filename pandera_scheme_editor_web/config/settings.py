"""Django settings for the Pandera schema editor web app.

This app is a local, single-operator tool with the same filesystem trust
level as the original GTK desktop app: whoever runs `manage.py runserver`
can read/write any YAML path it is given. It is not meant to be exposed
beyond localhost, and no authentication system is included on purpose.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-insecure-key-change-if-ever-exposed-beyond-localhost",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# Application definition
#
# No django.contrib.auth / django.contrib.admin: this tool has no user
# model and no admin need. Keeping them out avoids an unused User table
# and an unused login flow for a single-operator local tool.
INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "schema_editor",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "schema_editor.context_processors.working_src",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
#
# SQLite exists solely to back Django's session table (used only for
# flash messages - see schema_editor.context_processors and the views).
# To avoid the DB file entirely, set:
#   SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "es"

TIME_ZONE = "America/Mexico_City"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Schema editor settings
#
# Directory used for: (a) the workspace file-picker dropdown on the load
# screen, (b) where uploaded files get saved. Created lazily on first use.
SCHEMA_EDITOR_WORKSPACE_DIR = Path(
    os.environ.get("SCHEMA_EDITOR_WORKSPACE_DIR", str(BASE_DIR / "examples"))
)
