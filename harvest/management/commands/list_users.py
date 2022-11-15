from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from harvest.models import Harvest


class Command(BaseCommand):
    """Command showing list of users containing their id's and number of harvests"""

    def handle(self, *args, **options):
        # TODO implement
        pass
