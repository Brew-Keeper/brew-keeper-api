"""Settings to use in production Heroku deploy."""

import os

import dj_database_url

from .settings import *  # noqa

DEBUG = bool(int(os.environ.get("DEBUG", "0")))
SECRET_KEY = os.environ["SECRET_KEY"]

BLACKLIST_APPS = ["debugtoolbar", "django_extensions"]

INSTALLED_APPS = tuple(
    [app for app in INSTALLED_APPS if app not in BLACKLIST_APPS]  # noqa
)

DATABASES["default"] = dj_database_url.config()  # noqa

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ALLOWED_HOSTS = ["*"]

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = "staticfiles"
# STATIC_ROOT = os.path.join(os.getcwd(), "staticfiles")
STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

STATICFILES_STORAGE = "whitenoise.django.GzipManifestStaticFilesStorage"
