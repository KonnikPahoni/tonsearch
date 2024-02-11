from django.core.management.base import BaseCommand

from tonnftscan.models import Address
from tonnftscan.search import sync_google_search_queries
from indicators.services import calculate_daily_indicators_service, calculate_spam_indicators_service


class Command(BaseCommand):
    help = f"Scans the supplied address."

    def handle(self, *args, **options):
        calculate_spam_indicators_service()
