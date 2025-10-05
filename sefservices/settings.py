from pathlib import Path
import os
import locale

from decouple import config as env_config
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

DEBUG = env_config('DEBUG', cast=bool)
APP_NAME = env_config('APP_NAME')
PRODUCTION = env_config('PRODUCTION', cast=bool)


SECRET_KEY = 'django-insecure-r-#tu=!6=5n8-b==5jo70p545@uz0fa2-rgsqei9l_zqrhrsc9'

ALLOWED_HOSTS = env_config('ALLOWED_HOSTS').split(',')

SITE_URL = env_config('SITE_URL')

if PRODUCTION:
    CSRF_TRUSTED_ORIGINS = env_config('SITE_URL').split(',')
    SECURE_SSL_REDIRECT = True
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CONN_MAX_AGE = None

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 210 * 60  #

Q_CLUSTER = {
    'name': "mysaas",
    'workers': 2,  # Number of workers. Set as None to match CPU count
    'timeout': 60,  # Limit on how long a task is allowed to take, in seconds.
    'retry': 300,
    'orm': 'default',
    'save_limit': 0,
    "bulk": 10,
    "queue_limit": 50,
    'ack_failures': False,
    'max_attempts': 10,
    'log_level': 'DEBUG'
}


CAPTCHA_SITE_KEY = env_config('CAPTCHA_SITE_KEY')
CAPTCHA_SECRET_KEY = env_config('CAPTCHA_SECRET_KEY')

GOOGLE_MAP_API_KEY = env_config('GOOGLE_MAP_API_KEY')

# MinIO Configuration
AWS_ACCESS_KEY_ID = env_config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env_config('AWS_SECRET_ACCESS_KEY')
AWS_S3_ENDPOINT_URL = env_config('AWS_S3_ENDPOINT_URL')
AWS_S3_PREVIEW_URL = env_config('AWS_S3_PREVIEW_URL')
AWS_STORAGE_BUCKET_NAME = 'storesaas'
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_S3_ADDRESSING_STYLE = "path"

# --- Static Files ---
#STATICFILES_STORAGE = 'coreservice.storages.StaticStorage'
#STATIC_URL = f'{AWS_S3_PREVIEW_URL}/{AWS_STORAGE_BUCKET_NAME}/static/'

STATIC_URL = '/storage/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'fileassets')


# --- Media Files ---
DEFAULT_FILE_STORAGE = 'coreservice.storages.MediaStorage'
MEDIA_URL = f'{AWS_S3_PREVIEW_URL}/{AWS_STORAGE_BUCKET_NAME}/medias/'

# Réglages Email
MAIL_SENDER_NAME = env_config('MAIL_SENDER_NAME')
MAIL_API_KEY = env_config('MAIL_API_KEY')

# Link SMS Setting
SMS_CLIENT_ID = env_config('SMS_CLIENT_ID')
SMS_SECRET_KEY = env_config('SMS_SECRET_KEY')
SMS_SENDER_ID = env_config('SMS_SENDER_ID')
SMS_URL = env_config('SMS_URL')

# Stripe Settings
STRIPE_API_KEY = env_config('STRIPE_API_KEY')
STRIPE_PUBLIC_KEY = env_config('STRIPE_PUBLIC_KEY')
STRIPE_ENDPOINT_SECRET = env_config('STRIPE_ENDPOINT_SECRET')

# Google Login
SOCIAL_AUTH_GOOGLE_OAUTH_KEY = '528330824749-6988ohe7a44is581kr19sgkcebnps269.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH_SECRET = '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'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '528330824749-6988ohe7a44is581kr19sgkcebnps269.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['local_password',]
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {'approval_prompt': 'force'}
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ['email', 'name', 'first_name', 'last_name']

AUTH_USER_MODEL = "accounts.Customer"

AUTHENTICATION_BACKENDS = [
    'accounts.AuthBackend.UserAuthBackend',
    'social_core.backends.google.GoogleOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

# Social Auth Pipeline
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'coreservice.customer_pipeline.save_profile',  # Custom Pipeline to save user profile
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'coreservice.customer_pipeline.collect_password',  # Custom Pipeline to setnew password

)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'coreservice',
    'accounts',
    'rides',
    'payments',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sefservices.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'sefservices.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_config('DB_NAME'),
        'USER': env_config('DB_USER'),
        'PASSWORD': env_config('DB_PASSWORD'),
        'HOST': env_config('DB_HOST'),
        'PORT': env_config('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S'
]

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Africa/Lome'

USE_I18N = True           # Enable Django's i18n framework
USE_L10N = True           # Enable localized formatting
USE_TZ = True             # Timezone support

LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
    ('es', _('Spanish')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
