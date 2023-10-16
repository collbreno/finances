from django.core.management.base import BaseCommand

from finances.tasks import schedule_jobs

class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        schedule_jobs()