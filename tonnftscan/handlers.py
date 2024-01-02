import logging

from django.http import HttpResponse

from tonnftscan.models import Collection, NFT, Address
from tonnftscan.services import fetch_collection_service, fetch_nft_service, fetch_address_service
from tonnftscan.settings import BASE_DIR


def fetch_collections_handler():
    """
    Fetch all collections from tonscan.
    """
    for collection in Collection.objects.filter(last_fetched_at__isnull=True):
        logging.info(f"Processing collection {collection}...")
        fetch_collection_service(collection)
        logging.info(f"Collection {collection} processed.")


def fetch_addresses_handler():
    """
    Fetch all addresses of NFT holders via tonscan.
    """
    nfts_owners_list = list(NFT.objects.filter(owner__isnull=False).values_list("owner", flat=True).distinct())

    addresses_filterset = Address.objects.filter(address__in=nfts_owners_list, last_fetched_at=None)

    logging.info(f"Starting to process {addresses_filterset.count()} addresses...")

    for address_object in addresses_filterset:
        logging.info(f"Processing address {address_object}...")
        fetch_address_service(address_object)
        logging.info(f"Address {address_object} processed.")


def fetch_nfts_handler():
    """
    Fetch all nfts from tonscan.
    """
    for collection in Collection.objects.all():
        logging.info(f"Fetching NFTs for collection {collection}...")
        nfts_filterset = NFT.objects.filter(collection=collection, last_fetched_at__isnull=True)
        for nft in nfts_filterset:
            try:
                sale_owner_address = nft.sale["owner"]["address"]
            except KeyError:
                sale_owner_address = None

            logging.info(f"Processing nft {nft} for collection {collection}...")
            fetch_nft_service(nft)
            logging.info(f"NFT {nft} for collection {collection} processed.")


def get_sitemap_handler():
    """
    Return sitemap file response.
    """
    with open(BASE_DIR / "tonnftscan/static/sitemap.xml", "r", encoding="utf-8") as input_file:
        content = input_file.read()

    response = HttpResponse(content, content_type="application/xml")

    return response
