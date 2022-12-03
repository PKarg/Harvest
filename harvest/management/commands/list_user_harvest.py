from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from harvest.models import Harvest


class Command(BaseCommand):
    """Command showing list of harvests for specified user, all or with specified fruit or yaer"""
    help = "Command showing list of harvests for specified user, all or with specified fruit"

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='+', type=int)
        parser.add_argument('--fruit',
                            nargs='?',
                            type=str,
                            help="Filter by fruit")
        parser.add_argument('--year',
                            nargs='?',
                            type=int,
                            help="Filter by year")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options['user_id'][0])
            fruit = options.get('fruit')
            year = options.get('year')

            harvests = Harvest.objects.filter(owner=user)
            if fruit:
                harvests = harvests.filter(fruit=fruit)
            if year:
                harvests = harvests.filter(date__year=year)
            harvests = harvests.all()

            if harvests:
                self.stdout.write(f"User {harvests[0].owner.username} has {len(harvests)} Harvests"
                                  f" with specified parameters")
                for harvest in harvests:
                    self.stdout.write(f"{harvest.date} {harvest.fruit}, Amount harvested: {harvest.amount},"
                                      f" Price: {harvest.price}, Profit: {harvest.profits}")
            else:
                message = "Given user has no harvests with specified parameters" if fruit or year \
                    else "There are no Harvests for given user"
                self.stdout.write(message)

        except User.DoesNotExist:
            self.stdout.write("User with given id does not exist")
