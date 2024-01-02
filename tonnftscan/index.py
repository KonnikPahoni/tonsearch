import json
import logging

from django.utils import timezone
from oauth2client.service_account import ServiceAccountCredentials
import httplib2

from tonnftscan.models import Collection
from tonnftscan.settings import FIREBASE_CREDENTIALS

SCOPES = ["https://www.googleapis.com/auth/indexing"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(FIREBASE_CREDENTIALS), scopes=SCOPES)
http = credentials.authorize(httplib2.Http())


def send_page_to_google_index(url: str, collection: Collection):
    """
    Send person to Google index.
    """
    logging.info(f"Sending link {url} to Google index.")

    content = {"url": url, "type": "URL_UPDATED"}
    json_ctn = json.dumps(content)

    response, content = http.request(
        "https://indexing.googleapis.com/v3/urlNotifications:publish", method="POST", body=json_ctn
    )

    result = json.loads(content.decode())

    # For debug purpose only
    if "error" in result:
        logging.error(
            "Error({} - {}): {}".format(result["error"]["code"], result["error"]["status"], result["error"]["message"])
        )

        return None
    else:
        logging.info("urlNotificationMetadata.url: {}".format(result["urlNotificationMetadata"]["url"]))
        logging.info(
            "urlNotificationMetadata.latestUpdate.url: {}".format(
                result["urlNotificationMetadata"]["latestUpdate"]["url"]
            )
        )
        logging.info(
            "urlNotificationMetadata.latestUpdate.type: {}".format(
                result["urlNotificationMetadata"]["latestUpdate"]["type"]
            )
        )
        logging.info(
            "urlNotificationMetadata.latestUpdate.notifyTime: {}".format(
                result["urlNotificationMetadata"]["latestUpdate"]["notifyTime"]
            )
        )

        collection.pushed_to_google_at = timezone.now()
        collection.save()

        return collection
