import logging
import time
from datetime import datetime

import requests
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.exceptions import NotFound

from tonnftscan.constants import AddressType
from tonnftscan.models import Collection, Address, NFT, NFTTransactionAction
from tonnftscan.settings import TON_API_KEY
from tonnftscan.utils import convert_user_friendly_address_to_hex


def fetch_all_collections_service():
    """
    Fetch all TON NFT collections.
    """
    limit = 1000
    offset = 0

    while True:
        response = requests.get(
            "https://tonapi.io/v2/nfts/collections",
            params={
                "limit": limit,
                "offset": offset,
            },
            headers={
                "Authorization": f"Bearer {TON_API_KEY}",
            },
        )
        response_json = response.json()

        try:
            collections = response_json["nft_collections"]
        except KeyError:
            logging.error(f"Could not find nft_collections: {response_json}")
            break

        if len(collections) == 0:
            break

        offset += limit

        for collection in collections:
            logging.info(f"Processing collection {collection}...")

            try:
                address = collection["owner"]["address"]
                owner_address, _ = Address.objects.update_or_create(
                    address=address,
                    defaults={
                        "address": address,
                        "is_scam": collection["owner"]["is_scam"],
                    },
                )
            except KeyError:
                logging.error(f"Skipping collection {collection['address']}")
                owner_address = None

            try:
                social_links = (
                    collection["metadata"]["social_links"] if "social_links" in collection["metadata"].keys() else []
                )

                if not isinstance(social_links, list):
                    social_links = []

                if social_links is None:
                    social_links = []

                cover_image = (
                    collection["metadata"]["cover_image"] if "cover_image" in collection["metadata"].keys() else ""
                )
                if cover_image is None:
                    cover_image = ""

                collection_object, _ = Collection.objects.update_or_create(
                    address=collection["address"],
                    defaults={
                        "address": collection["address"],
                        "name": collection["metadata"]["name"] if "name" in collection["metadata"].keys() else "",
                        "description": collection["metadata"]["description"]
                        if "description" in collection["metadata"].keys()
                        else "",
                        "social_links": social_links,
                        "marketplace": collection["metadata"]["marketplace"]
                        if "marketplace" in collection["metadata"].keys()
                        else "",
                        "image": collection["metadata"]["image"] if "image" in collection["metadata"].keys() else "",
                        "cover_image": cover_image,
                        "external_url": (
                            collection["metadata"]["external_url"]
                            if "external_url" in collection["metadata"].keys()
                            else ""
                        )
                        or "",
                        "owner": owner_address,
                    },
                )
            except KeyError:
                logging.error(f"Skipping collection {collection['address']}")
                continue

            logging.debug(f"Collection {collection_object} updated.")


def fetch_collection_service(collection: Collection):
    """
    Fetch all TON NFTs in a collection.
    """
    limit = 1000
    offset = 0
    total_nfts = 0

    while True:
        time.sleep(1)
        response = requests.get(
            f"https://tonapi.io/v2/nfts/collections/{collection.address}/items",
            params={
                "limit": limit,
                "offset": offset,
            },
            headers={
                "Authorization": f"Bearer {TON_API_KEY}",
            },
        )

        try:
            response_json = response.json()
        except Exception as e:
            logging.error(f"Error parsing response: {e}. Response: {response.text}")
            continue

        logging.info(f"Processing collection {collection.address}...")

        try:
            nft_items = response_json["nft_items"]
        except KeyError:
            logging.error(f"Could not find nft_items for collection {collection.address}: {response_json}")
            break

        if len(nft_items) == 0:
            break

        offset += limit

        for NFT_item in nft_items:
            try:
                address = NFT_item["owner"]["address"]
                owner_address, _ = Address.objects.update_or_create(
                    address=address,
                    defaults={
                        "address": address,
                        "is_scam": NFT_item["owner"]["is_scam"],
                    },
                )
            except KeyError:
                logging.error(f"Skipping NFT {NFT_item['address']}")
                owner_address = None

            attributes = NFT_item["metadata"]["attributes"] if "attributes" in NFT_item["metadata"].keys() else []
            if attributes is None:
                attributes = []

            sale = NFT_item["sale"] if "sale" in NFT_item.keys() else dict()

            approved_by = str(NFT_item["approved_by"]) if "approved_by" in NFT_item.keys() else None

            description = NFT_item["metadata"]["description"] if "description" in NFT_item["metadata"].keys() else ""
            if description is None:
                description = ""

            nft_object, _ = NFT.objects.update_or_create(
                address=NFT_item["address"],
                defaults={
                    "address": NFT_item["address"],
                    "name": NFT_item["metadata"]["name"] if "name" in NFT_item["metadata"].keys() else "",
                    "description": description,
                    "image": NFT_item["metadata"]["image"] if "image" in NFT_item["metadata"].keys() else "",
                    "external_url": (
                        NFT_item["metadata"]["external_url"] if "external_url" in NFT_item["metadata"].keys() else ""
                    )
                    or "",
                    "attributes": attributes,
                    "owner": owner_address,
                    "collection": collection,
                    "sale": sale,
                    "verified": NFT_item["verified"],
                    "approved_by": approved_by,
                },
            )
            total_nfts += 1

    collection.last_fetched_at = timezone.now()
    collection.nfts_count = total_nfts
    collection.save()


def fetch_address_service(address: Address):
    """
    Fetch status and metadata of an address.
    """
    response = requests.get(
        f"https://tonapi.io/v2/accounts/{address.address}",
        headers={
            "Authorization": f"Bearer {TON_API_KEY}",
        },
    )
    logging.info(f"Processing address {address.address}: {response.text}")

    try:
        response_json = response.json()
    except Exception as e:
        logging.error(f"Error parsing response: {e}. Response: {response.text}")
        return

    if "balance" not in response_json.keys():
        logging.error(f"Could not fetch address {address.address}: {response_json}")
        return

    balance = response_json["balance"] if "balance" in response_json.keys() else None

    last_activity = response_json["last_activity"] if "last_activity" in response_json.keys() else None
    if last_activity is not None:
        last_activity = timezone.datetime.fromtimestamp(last_activity)

    status = response_json["status"] if "status" in response_json.keys() else None
    interfaces = response_json["interfaces"] if "interfaces" in response_json.keys() else []
    name = response_json["name"] if "name" in response_json.keys() else None
    is_scam = response_json["is_scam"] if "is_scam" in response_json.keys() else None
    icon = response_json["icon"] if "icon" in response_json.keys() else None

    # Identify address type based on interfaces
    address_type = None
    for interface in interfaces:
        if "wallet" in interface:
            address_type = AddressType.WALLET
            break

        if "nft_sale" in interface:
            address_type = AddressType.NFT_SALE
            break

    if balance is not None:
        address.balance = balance

    if last_activity is not None:
        address.last_activity = last_activity

    if status is not None:
        address.status = status

    address.interfaces = interfaces

    if name is not None:
        address.name = name

    if is_scam is not None:
        address.is_scam = is_scam

    if icon is not None:
        address.icon = icon

    address.address_type = address_type

    address.last_fetched_at = timezone.now()
    address.num_of_nft_transactions = (
        NFTTransactionAction.objects.filter(sender=address).count()
        + NFTTransactionAction.objects.filter(recipient=address).count()
    )
    address.nfts_count = NFT.objects.filter(owner=address).count()

    address.save()


def fetch_nft_service(nft: NFT):
    """
    Fetch transactions for a NFT.
    """
    limit = 1000

    response = requests.get(
        f"https://tonapi.io/v2/nfts/{nft.address}/history",
        params={
            "limit": limit,
        },
        headers={
            "Authorization": f"Bearer {TON_API_KEY}",
        },
    )
    response_json = response.json()
    try:
        events = response_json["events"]
    except KeyError:
        logging.error(f"Could not find events for NFT {nft.address}: {response_json}")
        return

    if len(events) > 1000:
        raise Exception(f"Too many events for NFT {nft.address}")

    for event in events:
        for action in event["actions"]:
            logging.debug(f"Processing action {action} for NFT {nft.address}...")
            action_type = action["type"]
            action_status = action["status"]
            nft_id = action[action_type]["nft"]

            if nft_id != nft.address:
                continue

            try:
                sender_address_hex = action[action_type]["sender"]["address"]
                sender_address, _ = Address.objects.update_or_create(
                    address=sender_address_hex,
                    defaults={
                        "address": sender_address_hex,
                        "is_scam": action[action_type]["sender"]["is_scam"],
                        "name": action[action_type]["sender"]["name"]
                        if "name" in action[action_type]["sender"].keys()
                        else None,
                    },
                )
            except KeyError:
                sender_address = None

            recipient_address_hex = action[action_type]["recipient"]["address"]

            recipient_address, _ = Address.objects.update_or_create(
                address=recipient_address_hex,
                defaults={
                    "address": recipient_address_hex,
                    "is_scam": action[action_type]["recipient"]["is_scam"],
                    "name": action[action_type]["recipient"]["name"]
                    if "name" in action[action_type]["recipient"].keys()
                    else None,
                },
            )

            transaction_action, _ = NFTTransactionAction.objects.update_or_create(
                transaction_hex=event["event_id"],
                nft=nft,
                sender=sender_address,
                recipient=recipient_address,
                defaults={
                    "transaction_hex": event["event_id"],
                    "nft": nft,
                    "sender": sender_address,
                    "recipient": recipient_address,
                    "status": action_status,
                    "type": action_type,
                    "timestamp": make_aware(datetime.utcfromtimestamp(event["timestamp"])),
                },
            )

    nft.last_fetched_at = timezone.now()
    nft.num_of_transactions = NFTTransactionAction.objects.filter(nft=nft, status="ok").count()

    # Identify the last recipient of the NFT
    try:
        last_transaction = NFTTransactionAction.objects.filter(nft=nft).order_by("-timestamp")[0]
        nft.owner = last_transaction.recipient
    except IndexError:
        pass

    nft.save()


def get_collection_for_address_service(collection_id: str) -> Collection:
    """
    Returns a collection for a given address.
    """
    if len(collection_id) == 66:
        # This is a hex address
        collection = Collection.objects.get(address=collection_id)
    elif len(collection_id) == 48:
        # This is a user-friendly address
        hex_address = convert_user_friendly_address_to_hex(collection_id)
        logging.debug(f"Converted {collection_id} to {hex_address}")
        collection = Collection.objects.get(address=hex_address)
    else:
        logging.error(f"Invalid collection ID: {collection_id}")

        raise NotFound(f"Invalid collection ID: {collection_id}")

    return collection


def get_nft_for_address_service(nft_id: str) -> NFT:
    """
    Returns a NFT for a given address.
    """
    if len(nft_id) == 66:
        # This is a hex address
        nft = NFT.objects.get(address=nft_id)
    elif len(nft_id) == 48:
        # This is a user-friendly address
        hex_address = convert_user_friendly_address_to_hex(nft_id)
        logging.debug(f"Converted {nft_id} to {hex_address}")
        nft = NFT.objects.get(address=hex_address)
    else:
        logging.error(f"Invalid NFT ID: {nft_id}")

        raise NotFound(f"Invalid NFT ID: {nft_id}")

    return nft


def get_wallet_for_address_service(wallet_id: str) -> Address:
    """
    Returns a wallet for a given address.
    """
    if len(wallet_id) == 66:
        # This is a hex address
        wallet = Address.objects.get(address=wallet_id)
    elif len(wallet_id) == 48:
        # This is a user-friendly address
        hex_address = convert_user_friendly_address_to_hex(wallet_id)
        logging.debug(f"Converted {wallet_id} to {hex_address}")
        wallet = Address.objects.get(address=hex_address)
    else:
        logging.error(f"Invalid wallet ID: {wallet_id}")

        raise NotFound(f"Invalid wallet ID: {wallet_id}")

    return wallet


def search_collections_service(query: str):
    """
    Searches for collections.
    """
    wallets = Collection.objects.filter(name__icontains=query).order_by("-last_fetched_at")

    return wallets


def search_nfts_service(query: str):
    """
    Searches for NFTs.
    """
    nfts = NFT.objects.filter(name__icontains=query).order_by("-last_fetched_at")

    return nfts


def search_wallets_service(query: str):
    """
    Searches for wallets.
    """
    addresses = Address.objects.filter(name__icontains=query).order_by("-last_fetched_at")

    return addresses
