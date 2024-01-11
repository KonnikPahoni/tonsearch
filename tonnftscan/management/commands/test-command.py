import base64
import logging

import tonsdk
from django.core.management.base import BaseCommand
from tonsdk.utils._utils import string_to_bytes

from tonnftscan.handlers import fetch_nfts_handler, fetch_addresses_handler
from tonnftscan.models import Collection, Address
from tonnftscan.services import fetch_all_collections_service, fetch_collection_service, fetch_address_service
from tonnftscan.utils import convert_user_friendly_address_to_hex


class Command(BaseCommand):
    help = f"Scans the supplied address."

    def handle(self, *args, **options):
        address = Address.objects.get(
            address=convert_user_friendly_address_to_hex("EQAhTh8UHr0yPDYYy7cCcwYynbVUjbEOe7KdCugYFrA_oAQR")
        )
        fetch_address_service(address)
