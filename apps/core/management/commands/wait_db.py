import time

from django.core.management import BaseCommand
from django.db import OperationalError, connection


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Waiting database...")
        db_ready = False

        while not db_ready:
            try:
                connection.ensure_connection()
                db_ready = True
            except OperationalError:
                self.stdout.write("Database unavailable, wait 3 seconds...")
                time.sleep(3)

        self.stdout.write(self.style.SUCCESS("Database available."))