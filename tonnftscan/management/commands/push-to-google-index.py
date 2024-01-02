import logging

from django.core.management.base import BaseCommand

from tonnftscan.index import send_page_to_google_index
from tonnftscan.models import Collection
from tonnftscan.utils import send_message_to_support_chat


class Command(BaseCommand):
    help = "Push pages to Google index."

    def handle(self, *args, **options):
        collections_to_push_data = Collection.objects.filter(pushed_to_google_at__isnull=True).order_by("-nfts_count")

        logging.info(f"Found {collections_to_push_data.count()} collections to push to Google index.")

        pushed = 0

        for collection in collections_to_push_data:
            search_data_object = send_page_to_google_index(collection.get_url(), collection)

            if search_data_object is None:
                logging.error(f"Error while pushing {collection} to Google index.")
                break
            else:
                pushed += 1

            break
        logging.info(f"Pushed {pushed} collections to Google index.")
        send_message_to_support_chat(f"Pushed {pushed} collections to Google index.")
