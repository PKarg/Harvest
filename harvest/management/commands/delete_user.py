from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    """Command to delete user by id"""
    help = "Command to delete user by id"

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for u_id in options['user_id']:
            try:
                self.stdout.write(f"Deleting user with id: {u_id}")
                user = User.objects.get(pk=u_id)
                user.delete()
                self.stdout.write(f"User {user.username} successfully deleted")

            except User.DoesNotExist:
                self.stdout.write(f"User with given id does not exist")
