import logging
import time
import traceback
from itertools import chain

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from tonnftscan.models import NFT
from tonnftscan.services import fetch_nft_service
from tonnftscan.utils import send_message_to_support_chat


class Command(BaseCommand):
    help = f"Fetched NFTS."

    FETCH_NFTS_EVERY_N_DAYS = 90

    def handle(self, *args, **options):
        time_start = timezone.now()
        last_fetched_at = timezone.now() - timezone.timedelta(days=self.FETCH_NFTS_EVERY_N_DAYS)

        # Create a filterset of NFTs that have not been fetched yet or have not been fetched for a long time
        nfts_filterset = NFT.objects.filter(Q(last_fetched_at__lte=last_fetched_at) | Q(last_fetched_at=None))

        logging.info(f"Found {nfts_filterset.count()} NFts to fetch.")

        nfts_fetched = 0
        nfts_to_fetch_max = 50000

        for nft in nfts_filterset[:nfts_to_fetch_max]:
            try:
                fetch_nft_service(nft)
                logging.info(f"Fetched NFT {nft.address}")
                nfts_fetched += 1
            except Exception as e:
                traceback_str = traceback.format_exc()
                logging.error(f"Failed to fetch NFT {nft.address} with error: {traceback_str}")
                send_message_to_support_chat(f"Failed to fetch {nft.address} with error: {e}")
                break
            time.sleep(1)

            if nfts_fetched % 100 == 0:
                logging.info(f"Fetched {nfts_fetched} NFTs.")

            if nfts_fetched >= nfts_to_fetch_max:
                logging.info(f"Fetched {nfts_fetched} NFTs. Stopping.")
                break

        time_end = timezone.now()

        message = f"Fetched {nfts_fetched} new NFTs at {time_end}. Took {(time_end - time_start).seconds / 60} min."
        send_message_to_support_chat(message, tech_chat=True)
