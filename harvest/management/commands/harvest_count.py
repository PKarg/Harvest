from django.core.management.base import BaseCommand, CommandError

from harvest.models import Harvest


class Command(BaseCommand):
    """Command showing count of harvests currently in database"""

    def handle(self, *args, **options):
        # TODO implement
        pass
