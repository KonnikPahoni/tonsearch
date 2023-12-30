from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequest(APIException):
    """
    General exception class for Bad Request 400 exceptions.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"
    default_code = "bad_request"
