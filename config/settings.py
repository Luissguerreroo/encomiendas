"""
Django settings for config project.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', cast=bool, default=False)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')


# ========================
# APPLICATIONS
# ========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'envios',
    'clientes',
    'rutas',

    # Django REST Framework y librerías API
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'corsheaders',
]

if DEBUG:
    INSTALLED_APPS += ['silk']


# ========================
# MIDDLEWARE
# ========================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    *(['silk.middleware.SilkyMiddleware'] if DEBUG else []),

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ========================
# URLS Y TEMPLATES
# ========================

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'envios.context_processors.estadisticas_globales',
            ],
        },
    },
]


# ========================
# LOCALIZACIÓN
# ========================

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Lima'

USE_I18N = True
USE_TZ = True


# ========================
# STATIC Y MEDIA
# ========================

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ========================
# WSGI / ASGI
# ========================

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = "config.asgi.application"


# ========================
# DATABASE
# ========================

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}


# ========================
# CHANNEL LAYERS (REDIS - VERSION AVANZADA)
# ========================

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {

            # ── Conexion ────────────────────────────────────────────
            'hosts': [REDIS_URL],

            # ── Identificacion ──────────────────────────────────────
            'prefix': 'encomiendas',

            # ── Mensajes ────────────────────────────────────────────
            'expiry': 60,
            'capacity': 100,

            # ── Capacidad por tipo de canal ─────────────────────────
            'channel_capacity': {
                'ws.connect.*': 200,
                'http.request': 200,
            },

            # ── Grupos ──────────────────────────────────────────────
            'group_expiry': 86400,

            # ── Seguridad (opcional) ────────────────────────────────
            # 'symmetric_encryption_keys': [os.environ.get('REDIS_SECRET')],
        },
    },
}

# ========================
# CHANNEL LAYERS (TESTING)
# ========================

if 'test' in sys.argv or 'pytest' in sys.modules:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }


# ========================
# AUTH / SESSIONS
# ========================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

SESSION_COOKIE_AGE = 60 * 60 * 8
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_NAME = 'encomiendas_session'


# ========================
# REST FRAMEWORK
# ========================

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# ========================
# JWT
# ========================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}


# ========================
# CORS
# ========================

CORS_ALLOW_ALL_ORIGINS = True


# ========================
# DEFAULT PK
# ========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'