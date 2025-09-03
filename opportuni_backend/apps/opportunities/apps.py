from django.apps import AppConfig


class OpportunitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.opportunities'

    def ready(self):
        """Import signals when the app is ready"""
        try:
            import apps.opportunities.signals  # noqa F401
        except ImportError:
            pass
