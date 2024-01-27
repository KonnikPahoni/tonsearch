import logging
import time
import traceback

from django.core.management.base import BaseCommand
from django.utils import timezone

from tonnftscan.models import NFT, Address
from tonnftscan.services import fetch_address_service
from tonnftscan.utils import send_message_to_support_chat


class Command(BaseCommand):
    help = f"Fetched wallets_to_fetch_max wallets."

    FETCH_WALLETS_EVERY_N_DAYS = 14

    def handle(self, *args, **options):
        time_start = timezone.now()

        owners_list = NFT.objects.all().values_list("owner", flat=True).distinct()

        last_fetched_at = timezone.now() - timezone.timedelta(days=self.FETCH_WALLETS_EVERY_N_DAYS)

        addresses_filterset = Address.objects.filter(address__in=owners_list, updated_at__lte=last_fetched_at)
        logging.info(f"Found {addresses_filterset.count()} addresses to fetch.")

        wallets_fetched = 0
        wallets_to_fetch_max = 25000

        for wallet in addresses_filterset:
            try:
                fetch_address_service(wallet)
                wallets_fetched += 1
            except Exception as e:
                traceback_str = traceback.format_exc()
                logging.error(f"Failed to fetch {wallet.address} with error: {traceback_str}")
                send_message_to_support_chat(f"Failed to fetch {wallet.address} with error: {e}")
                break
            time.sleep(1)

            if wallets_fetched % 1000 == 0:
                logging.info(f"Fetched {wallets_fetched} wallets.")

            if wallets_fetched >= wallets_to_fetch_max:
                logging.info(f"Fetched {wallets_fetched} wallets. Stopping.")
                break

        time_end = timezone.now()

        message = f"Fetched {addresses_filterset.count()} new wallets at {time_end}. Took {(time_end - time_start).seconds / 60} min."
        send_message_to_support_chat(message, tech_chat=True)
