# authapp/signals.py

import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    """
    Create a default admin user if it does not already exist.
    The admin credentials are provided via environment variables or default values.
    """
    User = get_user_model()
    admin_username = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
    admin_email = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "adminpassword")

    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
        )
        # Optionally print or log that the admin was created.
        print(f"Superuser '{admin_username}' created successfully.")
