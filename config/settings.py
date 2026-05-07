"""
Django settings for config project.
"""

from pathlib import Path
from decouple import config

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

    'envios',
    'clientes',
    'rutas',
]


# ========================
# MIDDLEWARE
# ========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

        # carpeta global templates/
        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Nuestro context processor personalizado:
                'envios.context_processors.estadisticas_globales',
            ],
        },
    },
]


# ========================
# STATIC Y MEDIA
# ========================

# URL base para archivos estáticos
STATIC_URL = 'static/'

# Carpetas en desarrollo
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Carpeta para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Archivos subidos por usuarios
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ========================
# WSGI
# ========================

WSGI_APPLICATION = 'config.wsgi.application'


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
# PASSWORDS
# ========================

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


# ========================
# INTERNACIONALIZACIÓN
# ========================

LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'

USE_I18N = True
USE_TZ = True


# ========================
# DEFAULT PK
# ========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================
# AUTENTICACIÓN
# ========================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ========================
# SESIONES
# ========================

# Duración: 8 horas
SESSION_COOKIE_AGE = 60 * 60 * 8

# No cerrar sesión al cerrar navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Nombre personalizado de la cookie
SESSION_COOKIE_NAME = 'encomiendas_session'