from django.apps import AppConfig


class CoreserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coreservice'

    def ready(self):
        import coreservice.receivers # noqa
        #import apps.signals
