from django.core.management.base import BaseCommand
from tonnftscan.search import sync_google_search_queries


class Command(BaseCommand):
    help = f"Scans the supplied address."

    def handle(self, *args, **options):
        sync_google_search_queries()
