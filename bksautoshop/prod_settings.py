import os


DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = []

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bksautoshop',
        'USER': 'bksadmin',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

# Время окончания приёма заявок
BID_TIME = {
    'hour': 14,
    'minute': 0,
    'second': 0,
    'microsecond': 0
}
