from django.core.management.base import BaseCommand, CommandError

from harvest.models import Harvest


class Command(BaseCommand):
    """Command showing count of harvests currently in database"""
    help = "Command showing count of harvests currently in database"

    def handle(self, *args, **options):
        all_harvests_count = Harvest.objects.count()
        self.stdout.write(f"Harvests in db: {all_harvests_count}")
