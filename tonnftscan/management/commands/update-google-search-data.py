import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from tonnftscan.search import sync_google_search_queries
from tonnftscan.utils import send_message_to_support_chat


class Command(BaseCommand):
    help = "Update data of the most popular pages."

    def handle(self, *args, **options):
        try:
            update_started = timezone.now()
            logging.info(f"Started updating search queries at {update_started}.")

            sync_google_search_queries()

            update_finished = timezone.now()
            logging.info(
                f"Finished updating search queries at {update_finished}. Took {(update_finished - update_started).seconds / 60} min."
            )
            send_message_to_support_chat(
                f"Updating SEO stats took {(update_finished - update_started).seconds / 60} min.", tech_chat=True
            )
        except Exception as e:
            logging.error(f"Failed to update search queries: {e}")
            send_message_to_support_chat(f"Failed to update search queries: {e}")
