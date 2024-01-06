from django.apps import AppConfig


class FooderpdblogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FoodERPDBLog'

    def ready(self):
        import FoodERPDBLog.routers  # Import the routers module to ensure the router is recognized
