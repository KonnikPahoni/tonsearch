from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = f"Scans the supplied address."

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write("Cleared cache\n")
