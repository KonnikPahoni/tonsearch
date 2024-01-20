import logging
import time
from itertools import chain

from django.core.management.base import BaseCommand
from django.utils import timezone

from tonnftscan.models import NFT
from tonnftscan.services import fetch_nft_service
from tonnftscan.utils import send_message_to_support_chat


class Command(BaseCommand):
    help = f"Fetched NFTS."

    FETCH_NFTS_EVERY_N_DAYS = 50

    def handle(self, *args, **options):
        time_start = timezone.now()
        last_fetched_at = timezone.now() - timezone.timedelta(days=self.FETCH_NFTS_EVERY_N_DAYS)

        nfts_filterset = NFT.objects.filter(last_fetched_at__lte=last_fetched_at)
        unfetched_nfts_filterset = NFT.objects.filter(last_fetched_at=None)
        logging.info(f"Found {nfts_filterset.count() + unfetched_nfts_filterset.count()} NFts to fetch.")

        nfts_fetched = 0
        nfts_to_fetch_max = 50000

        for nft in chain(unfetched_nfts_filterset, nfts_filterset):
            try:
                fetch_nft_service(nft)
                nfts_fetched += 1
            except Exception as e:
                logging.error(f"Failed to fetch {nft.address} with error: {e}")
                send_message_to_support_chat(f"Failed to fetch {nft.address} with error: {e}")
                break
            time.sleep(1)

            if nfts_fetched % 100 == 0:
                logging.info(f"Fetched {nfts_fetched} NFTs.")

            if nfts_fetched >= nfts_to_fetch_max:
                logging.info(f"Fetched {nfts_fetched} NFTs. Stopping.")
                break

        time_end = timezone.now()

        message = (
            f"Fetched {nfts_filterset.count()} new NFTs at {time_end}. Took {(time_end - time_start).seconds / 60} min."
        )
        send_message_to_support_chat(message, tech_chat=True)
