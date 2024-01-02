import base64
import logging

import tonsdk
from django.core.management.base import BaseCommand
from tonsdk.utils._address import parse_friendly_address, Address
from tonsdk.utils._utils import string_to_bytes

from tonnftscan.handlers import fetch_nfts_handler, fetch_addresses_handler
from tonnftscan.models import Collection
from tonnftscan.services import fetch_all_collections_service, fetch_collection_service


class Command(BaseCommand):
    help = f"Scans the supplied address."

    def handle(self, *args, **options):
        collections_filterset = Collection.objects.all()
        collections_filterset.update(last_fetched_at=None)

        for collection in Collection.objects.filter(last_fetched_at__isnull=True):
            logging.info(f"Processing collection {collection}...")
            fetch_collection_service(collection)
            logging.info(f"Collection {collection} processed.")
