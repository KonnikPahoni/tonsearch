import base64
import logging

import tonsdk
from django.core.management.base import BaseCommand
from tonsdk.utils._utils import string_to_bytes

from tonnftscan.handlers import fetch_nfts_handler, fetch_addresses_handler
from tonnftscan.models import Collection, Address, NFT
from tonnftscan.services import (
    fetch_all_collections_service,
    fetch_collection_service,
    fetch_address_service,
    fetch_nft_service,
)
from tonnftscan.utils import convert_user_friendly_address_to_hex


class Command(BaseCommand):
    help = f"Scans the supplied address."

    def handle(self, *args, **options):
        nft = NFT.objects.get(address="0:9438e31526e1432eb627e38ed4bb7c595e61e2370bb40fe7aca45c0cb7b3a79b")
        fetch_nft_service(nft)
