import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from tonnftscan.services import fetch_all_collections_service
from tonnftscan.utils import send_message_to_support_chat


class Command(BaseCommand):
    help = f"Fetched all collections."

    def handle(self, *args, **options):
        time_start = timezone.now()

        try:
            fetch_all_collections_service()
        except Exception as e:
            logging.error(f"Failed to fetch all collections: {e}")
            send_message_to_support_chat(
                f"Failed to fetch all collections after {(timezone.now() - time_start).seconds / 60} min: {e}"
            )

        time_end = timezone.now()

        logging.info(
            f"Finished fetching all collections at {time_end}. Took {(time_end - time_start).seconds / 60} min."
        )
