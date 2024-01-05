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

        addresses_filterset = Address.objects.filter(last_fetched_at__isnull=True, address__in=owners_list)

        for wallet in addresses_filterset:
            fetch_address_service(wallet)
            time.sleep(1)

        time_end = timezone.now()

        message = f"Fetched {addresses_filterset.count()} new wallets at {time_end}. Took {(time_end - time_start).seconds / 60} min."
        send_message_to_support_chat(message, tech_chat=True)
