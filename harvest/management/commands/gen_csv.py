import csv
import datetime
import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from harvest.models import Harvest


class Command(BaseCommand):
    """Command generating csv report with all harvests in database
       for specific user, fruit or year"""
    help = """Command generating csv report with all harvests in database
              for specific user, fruit or year"""

    def add_arguments(self, parser):
        parser.add_argument('--test',
                            nargs='?',
                            type=int,
                            help="Testing flag")

        parser.add_argument('--user-id',
                            nargs='?',
                            type=int,
                            help="Filter by user id")

        parser.add_argument('--fruit',
                            nargs='?',
                            type=str,
                            help="Filter by fruit")

        parser.add_argument('--year',
                            nargs='?',
                            type=int,
                            help="Filter by year")

    def handle(self, *args, **options):
        harvests = Harvest.objects

        filename_comp = []

        if options.get("test"):
            filename_comp.append("test")

        filename_comp.append('harvests')

        user_id = options.get('user_id')

        try:
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    harvests = harvests.filter(owner=user)
                    filename_comp.append(str(user_id))

                except User.DoesNotExist:
                    raise CommandError(f"User with given id ({user_id}) does not exist")

            fruit = options.get('fruit')
            if fruit:
                filename_comp.append(fruit)
                harvests = harvests.filter(fruit=fruit)
            year = options.get('year')

            if year:
                filename_comp.append(str(year))
                harvests = harvests.filter(date__year=year)
            harvests = harvests.all()

            csv_dir_path = os.path.join(os.getcwd(), "csv_out")

            if not os.path.exists(csv_dir_path):
                os.mkdir(csv_dir_path)
            filename = f"{'_'.join(filename_comp)}_{datetime.date.today()}.csv"
            with open(os.path.join(csv_dir_path,
                      filename),
                      mode="w+") as csv_file:
                writer = csv.writer(csv_file)
                header = [f.name for f in Harvest._meta.get_fields()]
                writer.writerow(header)
                for h in harvests:
                    row = []
                    for field in header:
                        row.append(getattr(h, field))
                    writer.writerow(row)

                self.stdout.write(f"Exported harvests to file {os.path.join(csv_dir_path, filename)}")

        except CommandError as e:
            self.stdout.write(f"User with given id ({user_id}) does not exist")
