import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

logger = logging.getLogger(__file__)
WERT66 = "wert66"

ADMIN = "admin"
USER = "user"


class Command(BaseCommand):
    help = "Initialize Data"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        User = get_user_model()

        if not User.objects.filter(username=ADMIN).exists():
            User.objects.create_superuser(ADMIN, password=WERT66)

        if not User.objects.filter(username=USER).exists():
            user = User.objects.create_user(USER, password=WERT66, is_staff=True)

            for class_str in ("dataset",):
                user.user_permissions.add(
                    Permission.objects.get(codename=f"view_{class_str}")
                )
                user.user_permissions.add(
                    Permission.objects.get(codename=f"add_{class_str}")
                )
                user.user_permissions.add(
                    Permission.objects.get(codename=f"change_{class_str}")
                )
