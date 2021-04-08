from __future__ import unicode_literals
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'edx_webhooks',
    'edx_webhooks_shopify',
    'edx_webhooks_woocommerce',
]
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    },
]
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'
ROOT_URLCONF = 'edx_webhooks.urls'
SECRET_KEY = "fake"
ALLOWED_HOSTS = ["*"]
DEBUG = False
