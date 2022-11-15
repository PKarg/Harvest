from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    """Command showing count of all non-admin users in the db"""

    def handle(self, *args, **options):
        # TODO implement
        pass
