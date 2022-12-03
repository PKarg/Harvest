from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from harvest.models import Harvest


class Command(BaseCommand):
    """Command showing list of users containing their id's and number of harvests"""
    help = "List all currently registered users with number of their harvests and date they registered"

    def handle(self, *args, **options):
        users = User.objects.all()
        if users:
            self.stdout.write(f"Registered users: {len(users)}")
            for user in users:
                n_user_harvests = Harvest.objects.filter(owner=user).count()
                self.stdout.write(f"Id: {user.id}, Username: {user.username},"
                                  f" Harvests: {n_user_harvests}, Date Joined: {user.date_joined.date()}\n")
        else:
            self.stdout.write(f"There are no registered users")
