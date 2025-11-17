from django.apps import AppConfig


class ZoneappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ZoneApp'
    def ready(self):
        import ZoneApp.signals  # Importa las señales para que se registren