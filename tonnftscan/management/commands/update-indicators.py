from django.core.management.base import BaseCommand
from tonnftscan.services import calculate_daily_indicators_service


class Command(BaseCommand):
    help = f"Updates daily indicators."

    def handle(self, *args, **options):
        calculate_daily_indicators_service()
