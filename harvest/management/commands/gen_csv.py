from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from harvest.models import Harvest


class Command(BaseCommand):
    """Command generating csv report with all harvests in database
       for specific user, fruit or both"""

    def handle(self, *args, **options):
        # TODO implement
        pass
