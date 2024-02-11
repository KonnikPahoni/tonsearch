import logging

from django.utils import timezone

from indicators.models import DailyIndicator, CollectionIndicators
from tonnftscan.constants import NULL_ADDRESSES_LIST
from tonnftscan.models import Collection, NFT, Address
from tonnftscan.utils import convert_user_friendly_address_to_hex


def calculate_daily_indicators_service():
    """
    Calculate daily indicators.
    """
    date = timezone.now().date()
    collections_count = Collection.objects.count()
    collection_nfts_count = NFT.objects.filter(collection__isnull=False).count()
    nft_holders_count = Address.objects.filter(nfts__isnull=False).distinct().count()
    nfts_on_sale_count = NFT.objects.exclude(sale={}).count()

    daily_indicator, created = DailyIndicator.objects.update_or_create(
        date=date,
        defaults={
            "date": date,
            "collections_count": collections_count,
            "collection_nfts_count": collection_nfts_count,
            "nft_holders_count": nft_holders_count,
            "nfts_on_sale_count": nfts_on_sale_count,
        },
    )
    if created is True:
        logging.info(f"Created daily indicator for {date}: {daily_indicator}")


def calculate_spam_indicators_service():
    """
    Calculate spam indicators.
    """
    collections = Collection.objects.all()

    null_addresses_hex_list = [
        convert_user_friendly_address_to_hex(null_address) for null_address in NULL_ADDRESSES_LIST
    ]

    null_addresses_list = Address.objects.filter(address__in=null_addresses_hex_list)

    for collection in collections:
        burned_nfts_count = collection.nfts.filter(owner__in=null_addresses_list).count()

        spam_ratio = burned_nfts_count / collection.nfts_count if collection.nfts_count > 0 else 0
        collection_indicators, _ = CollectionIndicators.objects.update_or_create(
            collection=collection,
            defaults={
                "collection": collection,
                "spam_ratio": spam_ratio,
            },
        )
