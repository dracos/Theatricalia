from django.apps import AppConfig
from django_cleanup.signals import cleanup_pre_delete
from sorl.thumbnail import delete


def sorl_delete(**kwargs):
    delete(kwargs['file'])


class PhotoConfig(AppConfig):
    name = 'photos'

    def ready(self):
        cleanup_pre_delete.connect(sorl_delete, dispatch_uid="photo_cleanup")
