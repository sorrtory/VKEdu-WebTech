from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Completely cleans up the database, remakes migrations, and applies them.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning up the database...")

        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
            tables = cursor.fetchall()
            for table in tables:
                self.stdout.write(f"Dropping table {table[0]}...")
                cursor.execute(f"DROP TABLE IF EXISTS \"{table[0]}\" CASCADE;")

        self.stdout.write(self.style.SUCCESS("Database cleanup complete."))

        self.stdout.write("Remaking migrations...")
        call_command('makemigrations')
        self.stdout.write(self.style.SUCCESS("Migrations remade successfully."))

        self.stdout.write("Applying migrations...")
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS("Migrations applied successfully."))