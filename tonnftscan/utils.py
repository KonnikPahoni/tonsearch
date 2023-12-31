import logging
import telegram
from tonsdk.utils import Address

from tonnftscan.settings import SITE_URL, ENV, TELEGRAM_TECH_CHAT_ID, TELEGRAM_SUPPORT_CHAT_ID, TELEGRAM_API_TOKEN

logging.info("Initializing Telegram bot...")
bot = telegram.Bot(TELEGRAM_API_TOKEN)
logging.info("Telegram bot initialized.")


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


def send_message_to_support_chat(message, tech_chat=False):
    """
    Sends a message to the support chat.
    """
    chat_id = TELEGRAM_TECH_CHAT_ID

    if ENV == "production" and tech_chat is False:
        chat_id = TELEGRAM_SUPPORT_CHAT_ID

    # Telegram has a limit of 4096 characters per message
    _message = message
    message_parts = []

    while len(_message) > 4090:
        max_length_message = _message[:4090]
        _message_parts = max_length_message.split("\n")
        del _message_parts[-1]
        max_length_message = "\n".join(_message_parts)
        message_parts.append(max_length_message)
        _message = _message.replace(max_length_message, "")

    message_parts.append(_message)

    for message_part in message_parts:
        logging.info(f"Sending message to Telegram: {message_part}")
        try:
            bot.send_message(chat_id, message_part, parse_mode="html")
        except Exception as e:
            logging.error(f"Could not send message to tech chat: {str(e)}. Retrying without ParseMode.HTML")
            bot.send_message(chat_id, message_part)
