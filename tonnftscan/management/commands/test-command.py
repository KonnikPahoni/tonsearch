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
        addr_str = "0:214e1f141ebd323c3618cbb7027306329db5548db10e7bb29d0ae81816b03fa0"
        address1 = Address(addr_str)
        print(address1.to_string(is_user_friendly=True))
        # result = parse_friendly_address(addr_str)
