import os

import dj_database_url


DEBUG = bool(os.environ.get('BKSAUTOSHOP_DEBUG', True))

SECRET_KEY = os.environ.get('BKSAUTOSHOP_SECRET_KEY')

ALLOWED_HOSTS = []

DATABASES = {'default': dj_database_url.config(env='BKSAUTOSHOP_DATABASE_URL', conn_max_age=500)}

# Время окончания приёма заявок
BID_TIME = {
    'hour': 14,
    'minute': 0,
    'second': 0,
    'microsecond': 0
}
