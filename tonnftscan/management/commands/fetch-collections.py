import logging

from django.core.management.base import BaseCommand

from tonnftscan.handlers import fetch_nfts_handler, fetch_addresses_handler
from tonnftscan.models import Collection
from tonnftscan.services import fetch_all_collections_service, fetch_collection_service


class Command(BaseCommand):
    help = f"Scans the supplied address."

    def handle(self, *args, **options):
        # fetch_all_collections_service()

        fetch_addresses_handler()
