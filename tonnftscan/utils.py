from tonsdk.utils import Address

from tonnftscan.settings import SITE_URL


def convert_hex_address_to_user_friendly(hex_address: str):
    """
    Convert hex address to user-friendly address.
    """

    address = Address(hex_address)

    return address.to_string(is_user_friendly=True, is_url_safe=True, is_bounceable=True)


def convert_user_friendly_address_to_hex(user_friendly_address: str):
    """
    Convert user-friendly address to hex address.
    """

    address = Address(user_friendly_address)

    return address.to_string(is_user_friendly=False, is_url_safe=True)


def get_base_context() -> dict:
    """
    Returns base context for all views.
    """
    base_context = {
        "site_url": SITE_URL,
    }

    return base_context
