from django.core.management.base import BaseCommand, CommandError

from harvest.models import Harvest


class Command(BaseCommand):
    """Command deleting harvests with specified ids"""
    help = "Command deleting harvests with specified id(s)"

    def add_arguments(self, parser):
        parser.add_argument('harvest_id', nargs='+', type=int)

    def handle(self, *args, **options):

        for h_id in options['harvest_id']:
            try:
                self.stdout.write(f"Deleting harvest with id {h_id}")
                harvest = Harvest.objects.get(pk=h_id)
                harvest.delete()
                self.stdout.write(f"Harvest {harvest} successfully deleted")

            except Harvest.DoesNotExist:
                self.stdout.write(f"Harvest with id {h_id} does not exist")
