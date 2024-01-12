import logging
import time
from django.core.management.base import BaseCommand
from django.utils import timezone

from tonnftscan.models import NFT, Address
from tonnftscan.services import fetch_address_service
from tonnftscan.utils import send_message_to_support_chat


class Command(BaseCommand):
    help = f"Fetched all wallets."

    def handle(self, *args, **options):
        time_start = timezone.now()

        owners_list = NFT.objects.all().values_list("owner", flat=True).distinct()

        last_fetched_at = timezone.now() - timezone.timedelta(days=3)

        addresses_filterset = Address.objects.filter(address__in=owners_list, updated_at__lte=last_fetched_at)
        logging.info(f"Found {addresses_filterset.count()} addresses to fetch.")

        for wallet in addresses_filterset:
            try:
                fetch_address_service(wallet)
            except Exception as e:
                logging.error(f"Failed to fetch {wallet.address} with error: {e}")
                send_message_to_support_chat(f"Failed to fetch {wallet.address} with error: {e}")
                break
            time.sleep(1)

        time_end = timezone.now()

        message = f"Fetched {addresses_filterset.count()} new wallets at {time_end}. Took {(time_end - time_start).seconds / 60} min."
        send_message_to_support_chat(message, tech_chat=True)
