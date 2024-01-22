import logging

from django.http import RawPostDataException

from tonnftscan.settings import logger, ENV


class GoogleLoggingMiddleware:
    """
    Middleware to send out log records to Google Logging
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        log_entry = {"REQUEST_METHOD": request.META["REQUEST_METHOD"], "PATH_INFO": request.META["PATH_INFO"]}

        try:
            log_entry["HTTP_X_FORWARDED_FOR"] = request.META["HTTP_X_FORWARDED_FOR"]
        except KeyError:
            log_entry["REMOTE_ADDR"] = request.META.get("REMOTE_ADDR")

        try:
            log_entry["REQUEST_BODY"] = str(request.body.decode("utf-8"))
        except UnicodeDecodeError:
            log_entry["REQUEST_BODY"] = "Cannot decode body."

        # Don't access POST data in middleware
        except RawPostDataException:
            # Get data from "POST" dictionary
            if request.META["REQUEST_METHOD"] == "POST":
                log_entry["POST"] = request.POST

        response = self.get_response(request)

        log_entry["RESPONSE_STATUS_CODE"] = str(response.status_code)

        try:
            log_entry["RESPONSE_DATA"] = str(response.data)
        except AttributeError:
            log_entry["CONTENT_TYPE"] = response["Content-Type"]

        # Disable logging to Google in tests
        if ENV not in ("test", "dev"):
            try:
                logger.log_struct(log_entry)
            except Exception as e:
                if "exceeds maximum size" in str(e):
                    log_entry["REQUEST_BODY"] = "Too large to log."
                    log_entry["RESPONSE_DATA"] = "Too large to log."
                    logger.log_struct(log_entry)
                else:
                    logging.error(f"Error logging to Google: {e}")

        return response
