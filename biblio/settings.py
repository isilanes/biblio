import os
import json
from pathlib import Path

from django_components import ComponentsSettings


PROJECT_NAME = "biblio"

# You can specify multiple configuration files to be checked in order.
# The first one found will be used.
try_confs = [
    os.environ.get("DJANGO_BIBLIO_CONF"),
    os.path.join(os.environ["HOME"], f".{PROJECT_NAME}.json"),
]

# Get configuration from JSON file (or keep default, empty):
conf = {}
for conf_file in try_confs:
    if conf_file and os.path.isfile(conf_file):
        with open(conf_file, 'r') as f:
            conf = json.load(f)
        break

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = conf.get("SECRET_KEY") or os.environ.get("DJANGO_SECRET_KEY")
DEBUG = conf.get("DEBUG") or (os.environ.get("DEBUG") == "True")
ALLOWED_HOSTS = conf.get("ALLOWED_HOSTS") or ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    PROJECT_NAME,
    "rest_framework",
    "django_components",
    "tailwind",
    "django_browser_reload",
]

MY_APPS = [
    "apps.theme",
    "apps.login",
    "apps.books",
    "apps.readings",
]
INSTALLED_APPS += MY_APPS

# Get extra apps either from JSON config (local), or from env variable (heroku):
# (I do not remember why I did that. Probably better to hardcode all apps in MY_APPS)
EXTRA_APPS = conf.get("EXTRA_APPS") or [a for a in os.environ.get("INSTALLED_APPS", "").split(":") if a]  # noqa
if EXTRA_APPS:
    INSTALLED_APPS += EXTRA_APPS

COMPONENTS = ComponentsSettings(
    autodiscover=True,
    reload_on_file_change=True,
    dirs=[
        BASE_DIR.joinpath("apps/books/components/mobile"),
    ],
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_components.middleware.ComponentDependencyMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = f'{PROJECT_NAME}.urls'
API_URLCONF = "config.urls."

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_PATH, "templates")],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            "loaders": [(
                'django.template.loaders.cached.Loader', [
                    # Default Django loader
                    'django.template.loaders.filesystem.Loader',
                    # Including this is the same as APP_DIRS=True
                    'django.template.loaders.app_directories.Loader',
                    # Components loader
                    'django_components.template_loader.Loader',
                ]
            )],
        },
    },
]
WSGI_APPLICATION = f'{PROJECT_NAME}.wsgi.application'

AVAILABLE_DATABASES = {
    'heroku': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd8jc2u569ga6jt',
    },
    'sqlite3': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': conf.get("DB_FILE"),
    },
    'local-pg': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': conf.get("DB_NAME", PROJECT_NAME),
        'USER': conf.get("DB_USER"),
        'PASSWORD': conf.get("DB_PASSWORD"),
        'HOST': conf.get("DB_HOST", "localhost"),
        'PORT': conf.get("DB_PORT", 5432),
    },
}
DATABASES = {}

if conf.get("WHICH_DB"):
    DATABASES["default"] = AVAILABLE_DATABASES[conf.get("WHICH_DB")]
else:
    # Heroku: Update database configuration from $DATABASE_URL.
    import dj_database_url  # noqa
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES["default"] = AVAILABLE_DATABASES["heroku"]
    DATABASES['default'].update(db_from_env)

# Password validation:
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization:
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# DRF:
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

# Static files:
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = []  # leave empty if static files only within apps (automatically found)
STATICFILES_FINDERS = [
    # Default finders
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # Django components
    "django_components.finders.ComponentsFileSystemFinder",
]

# Other:
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/books"
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
CSRF_TRUSTED_ORIGINS = ["https://goblin-fleet-escargot.ngrok-free.app"]  # for ngrok
TAILWIND_APP_NAME = "apps.theme"
