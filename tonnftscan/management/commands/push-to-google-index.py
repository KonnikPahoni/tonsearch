import logging

from django.core.management.base import BaseCommand

from tonnftscan.utils import send_message_to_support_chat


class Command(BaseCommand):
    help = "Push pages to Google index."

    def handle(self, *args, **options):
        persons_to_push_data = SearchData.objects.filter(
            pushed_to_google_at__isnull=True, person__checked=True, person__hidden=False, person__deleted=False
        ).order_by("-person__created_at")

        logging.info(f"Found {persons_to_push_data.count()} records to push to Google index.")

        pushed = 0

        for person_search_data in persons_to_push_data:
            search_data_object = send_person_to_google_index(person_search_data.person)

            if search_data_object is None:
                logging.error(f"Error while pushing {person_search_data.person} to Google index.")
                break
            else:
                pushed += 1

        logging.info(f"Pushed {pushed} records to Google index.")
        send_message_to_support_chat(f"Pushed {pushed} collections to Google index.")
