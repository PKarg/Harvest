from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    """Command to delete user by id"""

    def handle(self, *args, **options):
        # TODO implement
        pass
