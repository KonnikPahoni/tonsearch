import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from tonnftscan.models import Collection
from tonnftscan.services import fetch_all_collections_service, fetch_collection_service
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

        collections_filterset = Collection.objects.filter(last_fetched_at__isnull=True)

        for collection in collections_filterset:
            logging.info(f"Processing collection {collection}...")
            fetch_collection_service(collection)
            logging.info(f"Collection {collection} processed.")

        message = f"Fetched {collections_filterset.count()} new collections at {time_end}."
        send_message_to_support_chat(message, tech_chat=True)
