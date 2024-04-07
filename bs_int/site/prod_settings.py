from .settings import *  # noqa

ALLOWED_HOSTS = ['bsint', 'comet.dyndns.info']
CSRF_TRUSTED_ORIGINS = ['https://comet.dyndns.info']

MEDIA_ROOT = '/images-dir'
MEDIA_URL = '/images/'
