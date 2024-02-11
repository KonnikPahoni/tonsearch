import logging
from datetime import datetime

from django.utils import timezone
from rest_framework.exceptions import NotFound

from tonnftscan import searchconsole
from indicators.models import CollectionIndicators
from tonnftscan.services import get_collection_for_address_service
from tonnftscan.settings import TONSEARCH_URL

add_site = searchconsole.sites().add(siteUrl=TONSEARCH_URL).execute()
logging.info(f"Add site {TONSEARCH_URL}: {add_site}")
get_site = searchconsole.sites().get(siteUrl=TONSEARCH_URL).execute()
logging.info(f"Get site {TONSEARCH_URL}: {get_site}")


def execute_request(service, property_uri, request):
    """Executes a searchAnalytics.query request.

    Args:
      service: The searchconsole service to use when executing the query.
      property_uri: The site or app URI to request data for.
      request: The request to be executed.

    Returns:
      An array of response rows.
    """
    return service.searchanalytics().query(siteUrl=property_uri, body=request).execute()


def sync_google_search_queries():
    # Get all-time results
    search_results = get_collection_search_for_interval_service(
        start_datetime=datetime(2024, 1, 10),
        end_datetime=timezone.now(),
    )

    for key, item in search_results.items():
        try:
            collection = get_collection_for_address_service(key)
        except NotFound:
            logging.error(f"Could not find collection {key}")
            continue

        collection_search, _ = CollectionIndicators.objects.update_or_create(
            collection=collection,
            defaults={
                "collection": collection,
                "google_impressions_total": item["impressions"],
                "google_clicks_total": item["clicks"],
                "google_ctr_total": item["ctr"],
                "google_position_total": item["position"],
            },
        )

        logging.info(f"Updated search data for collection {collection}.")

    # Get 30-days results
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=30)

    search_results = get_collection_search_for_interval_service(
        start_datetime=start_date,
        end_datetime=end_date,
    )

    for key, item in search_results.items():
        try:
            collection = get_collection_for_address_service(key)
        except NotFound:
            logging.error(f"Could not find collection {key}")
            continue

        collection_search, _ = CollectionIndicators.objects.update_or_create(
            collection=collection,
            defaults={
                "collection": collection,
                "google_impressions_last_30_days": item["impressions"],
                "google_clicks_last_30_days": item["clicks"],
                "google_ctr_last_30_days": item["ctr"],
                "google_position_last_30_days": item["position"],
            },
        )

        logging.info(f"Updated 30-days search data for collection {collection}.")


def get_collection_search_for_interval_service(start_datetime: datetime, end_datetime: datetime):
    """
    Get search data for a given interval.
    """
    request = {
        "startDate": start_datetime.strftime("%Y-%m-%d"),
        "endDate": end_datetime.strftime("%Y-%m-%d"),
        "dimensions": ["page"],
        "rowLimit": 20000,
    }
    logging.info(f"Requesting search data for {TONSEARCH_URL} between {start_datetime} and {end_datetime}...")
    response = execute_request(searchconsole, f"{TONSEARCH_URL}/", request)
    logging.info(f"Got response: {response}")

    search_results = {}

    for page in response["rows"] if "rows" in response else []:
        if f"{TONSEARCH_URL}/collection/" in page["keys"][0]:
            collection_id = page["keys"][0].split("/")[-1]
            search_results[collection_id] = {
                "impressions": page["impressions"],
                "clicks": page["clicks"],
                "ctr": page["ctr"],
                "position": page["position"],
            }

    return search_results
