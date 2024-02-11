import logging

from django.utils import timezone

from indicators.models import DailyIndicator, CollectionIndicators, CollectionIndicatorsPercentiles
from tonnftscan.constants import NULL_ADDRESSES_LIST
from tonnftscan.models import Collection, NFT, Address, NFTTransactionAction
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


def calculate_burn_ratio_indicators_service():
    """
    Calculate burn ratio indicators.
    """
    null_addresses_hex_list = [
        convert_user_friendly_address_to_hex(null_address) for null_address in NULL_ADDRESSES_LIST
    ]

    null_addresses_list = Address.objects.filter(address__in=null_addresses_hex_list)

    null_address_nfts = NFT.objects.filter(owner__in=null_addresses_list)
    logging.info(f"Null address NFTs: {null_address_nfts.count()}")

    collections_with_burned_nfts = Collection.objects.filter(nfts__in=null_address_nfts).distinct()
    logging.info(f"Collections with burned NFTs: {collections_with_burned_nfts.count()}")

    for collection in collections_with_burned_nfts:
        burned_nfts_count = null_address_nfts.filter(collection=collection).count()

        burn_ratio = burned_nfts_count / collection.nfts_count if collection.nfts_count > 0 else None
        collection_indicators, _ = CollectionIndicators.objects.update_or_create(
            collection=collection,
            defaults={
                "collection": collection,
                "burn_ratio": burn_ratio,
            },
        )

        logging.debug(f"Calculated burn ratio for {collection}: {collection_indicators}")


def calculate_spam_factor_indicators_service():
    """
    Calculate spam factor indicators.
    """
    null_addresses_hex_list = [
        convert_user_friendly_address_to_hex(null_address) for null_address in NULL_ADDRESSES_LIST
    ]
    null_addresses_list = Address.objects.filter(address__in=null_addresses_hex_list)

    null_address_nfts = NFT.objects.filter(owner__in=null_addresses_list)
    logging.info(f"Null address NFTs: {null_address_nfts.count()}")

    collections_with_burned_nfts = Collection.objects.filter(nfts__in=null_address_nfts).distinct()
    logging.info(f"Collections with burned NFTs: {collections_with_burned_nfts.count()}")

    for collection in Collection.objects.filter(
        address="0:f39e2bc927931573cf49938898b44cd2462fc50fed11eaeaf385270a05c86465"
    ):
        users_who_burned_nfts_count = (
            NFTTransactionAction.objects.filter(
                nft__in=collection.nfts.all(),
                recipient__in=null_addresses_list,
            )
            .values("sender")
            .distinct()
            .count()
        )
        print(
            NFTTransactionAction.objects.filter(
                nft__in=collection.nfts.all(),
                recipient__in=null_addresses_list,
            )
            .values("sender")
            .distinct()
        )

        collection_indicators, _ = CollectionIndicators.objects.update_or_create(
            collection=collection,
            defaults={
                "collection": collection,
                "spam_factor": users_who_burned_nfts_count,
            },
        )

        logging.debug(f"Calculated spam factor for {collection}: {collection_indicators}")


def calculate_spread_ratio_indicator_service():
    """
    Calculate spread ratio indicator.
    """
    collections = Collection.objects.all()
    logging.info(f"Collections with no spread ratio: {collections.count()}")

    for collection in collections:
        nfts = NFT.objects.filter(collection=collection)
        nft_owners = Address.objects.filter(nfts__in=nfts).distinct()

        spread_ratio = nft_owners.count() / nfts.count() if nfts.count() > 0 else None

        collection_indicators, created = CollectionIndicators.objects.update_or_create(
            collection=collection,
            defaults={
                "collection": collection,
                "spread_ratio_current": spread_ratio,
            },
        )

        if created is True:
            logging.debug(f"Created spread ratio indicator for {collection}: {collection_indicators}")
        else:
            logging.debug(f"Updated spread ratio indicator for {collection}: {collection_indicators}")


def calculate_percentiles():
    """
    Calculate percentiles for collection indicators.
    """
    for collection in Collection.objects.filter(
        address="0:f39e2bc927931573cf49938898b44cd2462fc50fed11eaeaf385270a05c86465"
    ):
        try:
            collection_indicators = CollectionIndicators.objects.get(collection=collection)
        except CollectionIndicators.DoesNotExist:
            logging.warning(f"No indicators for {collection}")
            continue

        if collection_indicators.spam_factor is not None:
            spam_ratio_percentile = (
                CollectionIndicators.objects.filter(
                    spam_ratio__isnull=False, spam_ratio__lte=collection_indicators.spam_factor
                ).count()
                / CollectionIndicators.objects.filter(spam_ratio__isnull=False).count()
            )
        else:
            spam_ratio_percentile = None

        if collection_indicators.spread_ratio_current is not None:
            spread_ratio_percentile = (
                CollectionIndicators.objects.filter(
                    spread_ratio_current__isnull=False,
                    spread_ratio_current__lte=collection_indicators.spread_ratio_current,
                ).count()
                / CollectionIndicators.objects.filter(spread_ratio_current__isnull=False).count()
            )
        else:
            spread_ratio_percentile = None

        collection_indicators_percentiles, created = CollectionIndicatorsPercentiles.objects.update_or_create(
            collection=collection,
            defaults={
                "collection": collection,
                "spam_ratio": spam_ratio_percentile,
                "spread_ratio_current": spread_ratio_percentile,
            },
        )

        if created is True:
            logging.debug(f"Created percentiles for {collection}: {collection_indicators_percentiles}")
        else:
            logging.debug(f"Updated percentiles for {collection}: {collection_indicators_percentiles}")
