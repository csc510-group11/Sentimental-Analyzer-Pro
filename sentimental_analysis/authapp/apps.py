# authapp/apps.py

from django.apps import AppConfig

class AuthappConfig(AppConfig):
    name = 'authapp'

    def ready(self):
        # Import the signals so they get registered
        import authapp.signals
