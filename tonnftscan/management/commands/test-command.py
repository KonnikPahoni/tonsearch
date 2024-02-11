from django.core.management.base import BaseCommand

from tonnftscan.handlers import fetch_collection_nfts_handler
from tonnftscan.models import Address, Collection
from tonnftscan.search import sync_google_search_queries
from indicators.services import (
    calculate_daily_indicators_service,
    calculate_spread_ratio_indicator_service,
    calculate_percentiles,
    calculate_burn_ratio_indicators_service,
    calculate_spam_factor_indicators_service,
)


class Command(BaseCommand):
    help = f"Scans the supplied address."

    def handle(self, *args, **options):
        collection = Collection.objects.get(
            address="0:f39e2bc927931573cf49938898b44cd2462fc50fed11eaeaf385270a05c86465"
        )
        # fetch_collection_nfts_handler(collection)
        calculate_spam_factor_indicators_service()
