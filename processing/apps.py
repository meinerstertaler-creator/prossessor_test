from django.apps import AppConfig


class ProcessingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "processing"
    verbose_name = "Verfahren"

    def ready(self):
        import processing.signals  # noqa: F401