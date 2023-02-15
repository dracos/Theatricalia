from django.apps import AppConfig
from django_cleanup.signals import cleanup_pre_delete
from sorl.thumbnail import delete


class PhotoConfig(AppConfig):
    name = 'photos'


def sorl_delete(**kwargs):
    delete(kwargs['file'])


cleanup_pre_delete.connect(sorl_delete)
