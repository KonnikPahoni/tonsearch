import logging

from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import RedirectView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.template import loader
import jwt
import time
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from tonnftscan.constants import REL_NOFOLLOW_EXCEPTIONS, AddressType
from tonnftscan.handlers import get_sitemap_handler
from tonnftscan.models import Collection, NFT, Address, DailyIndicator
from tonnftscan.services import (
    get_collection_for_address_service,
    get_nft_for_address_service,
    get_wallet_for_address_service,
    search_collections_service,
    search_nfts_service,
    search_wallets_service,
    fetch_nft_service,
    fetch_address_service,
)
from tonnftscan.settings import METABASE_EMBED_KEY, METABASE_SITE_URL, SITE_URL, BASE_DIR
from tonnftscan.utils import (
    get_base_context,
    proxy_image_file_service,
    convert_hex_address_to_user_friendly,
    get_default_image_content,
)


class IndexView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request):
        """
        Returns a welcome page for the project.
        """

        template = loader.get_template("index.html")

        collections_filterset = Collection.objects.filter(
            last_fetched_at__isnull=False, collection_search__isnull=False
        ).order_by("-collection_search__google_impressions_last_30_days")

        collections_context = [collection.get_context() for collection in collections_filterset[:16]]

        # Get indicator with the latest date
        last_indicator = DailyIndicator.objects.order_by("-date").first()

        context = {
            **get_base_context(),
            "collections_num": last_indicator.collections_count,
            "nfts_num": last_indicator.collection_nfts_count,
            "wallets_num": last_indicator.nft_holders_count,
            "nfts_on_sale_num": last_indicator.nfts_on_sale_count,
            "collections": collections_context,
        }

        return HttpResponse(template.render(context, request))


class CollectionsView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, page_number=1):
        """
        Returns the collections page.
        """
        template = loader.get_template("collections.html")
        objects_per_page = 16

        base_context = get_base_context()

        collections_filterset = Collection.objects.filter(last_fetched_at__isnull=False, nfts_count__gt=0).order_by(
            "-nfts_count"
        )
        # Sort by the number of addresses that own NFTs from the collection
        # collections_filterset = collections_filterset.annotate(num_addresses=Count("nfts__owner", distinct=True))
        # collections_filterset = collections_filterset.order_by("-num_addresses")

        paginator = Paginator(collections_filterset, objects_per_page)

        try:
            # Get the objects for the requested page
            objects = paginator.page(page_number)
        except PageNotAnInteger:
            # If the page parameter is not an integer, display the first page
            objects = paginator.page(1)
        except EmptyPage:
            # If the page is out of range, display the last page
            return HttpResponseRedirect(reverse("collections", args=[paginator.num_pages]))

        collections = [collection.get_context() for collection in objects]

        context = {
            **base_context,
            "collections": collections,
            "previous_page_number": page_number - 1 if page_number > 1 else None,
            "page_number": page_number,
            "next_page_number": page_number + 1 if page_number < paginator.num_pages else None,
            "num_of_pages": paginator.num_pages,
            "total_collections": collections_filterset.count(),
        }

        return HttpResponse(template.render(context, request))


class NFTsView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, page_number=1):
        """
        Returns the NFTs page.
        """
        last_indicator = DailyIndicator.objects.order_by("-date").first()
        logging.info(f"Request: {request}")
        template = loader.get_template("nfts.html")
        base_context = get_base_context()

        objects_per_page = 16

        nfts_filterset = NFT.objects.order_by("-num_of_transactions")

        paginator = Paginator(nfts_filterset, objects_per_page)

        try:
            # Get the objects for the requested page
            objects = paginator.page(page_number)
        except PageNotAnInteger:
            # If the page parameter is not an integer, display the first page
            objects = paginator.page(1)
        except EmptyPage:
            # If the page is out of range, display the last page
            objects = paginator.page(paginator.num_pages)

        nfts = [nft.get_context(with_collection=False) for nft in objects]

        context = {
            **base_context,
            "nfts": nfts,
            "page_number": page_number,
            "previous_page_number": page_number - 1 if page_number > 1 else None,
            "next_page_number": page_number + 1 if page_number < paginator.num_pages else None,
            "num_of_pages": paginator.num_pages,
            "total_nfts": last_indicator.collection_nfts_count,
        }

        return HttpResponse(template.render(context, request))


class AddressesView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, page_number=1):
        """
        Returns the addresses page.
        """

        template = loader.get_template("addresses.html")
        base_context = get_base_context()

        objects_per_page = 16

        addresses_filterset = Address.objects.order_by("-nfts_count", "icon")

        paginator = Paginator(addresses_filterset, objects_per_page)

        try:
            # Get the objects for the requested page
            objects = paginator.page(page_number)
        except PageNotAnInteger:
            # If the page parameter is not an integer, display the first page
            objects = paginator.page(1)
        except EmptyPage:
            # If the page is out of range, display the last page
            objects = paginator.page(paginator.num_pages)

        wallets = [wallet.get_context(with_nfts=False) for wallet in objects]

        context = {
            **base_context,
            "wallets": wallets,
            "page_number": page_number,
            "previous_page_number": page_number - 1 if page_number > 1 else None,
            "next_page_number": page_number + 1 if page_number < paginator.num_pages else None,
            "num_of_pages": paginator.num_pages,
            "total_wallets": addresses_filterset.count(),
        }

        return HttpResponse(template.render(context, request))


class CollectionView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, collection_id):
        """
        Returns the collection page.
        """

        template = loader.get_template("collection.html")

        base_context = get_base_context()
        collection = get_collection_for_address_service(collection_id)

        collection_context = collection.get_context()

        popular_nfts = NFT.objects.filter(collection=collection).order_by("-created_at")[:12]
        popular_nfts = [nft.get_context() for nft in popular_nfts]

        try:
            owner_context = collection.owner.get_context()
        except AttributeError:
            owner_context = None

        context = {
            **collection_context,
            **base_context,
            "owner": owner_context,
            "allow_links": True
            if convert_hex_address_to_user_friendly(collection.address) in REL_NOFOLLOW_EXCEPTIONS
            else False,
            "popular_nfts": popular_nfts,
        }
        logging.info(f"Context for collection: {context}")

        return HttpResponse(template.render(context, request))


class NFTView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, nft_id):
        """
        Returns the NFT page.
        """

        template = loader.get_template("nft.html")

        base_context = get_base_context()
        nft = get_nft_for_address_service(nft_id)

        if nft.last_fetched_at is None or timezone.now() - nft.last_fetched_at > timezone.timedelta(days=7):
            fetch_nft_service(nft)

        nft_context = nft.get_context()

        context = {
            **nft_context,
            **base_context,
            "owner": nft.owner.get_context(with_nfts=False) if nft.owner else None,
            "collection_owner": nft.collection.owner.get_context(with_nfts=False) if nft.collection.owner else None,
        }
        logging.info(f"Context for nft: {context}")

        return HttpResponse(template.render(context, request))


class AddressView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, wallet_id):
        """
        Returns the page for an address.
        """

        template = loader.get_template("address.html")

        base_context = get_base_context()
        wallet = get_wallet_for_address_service(wallet_id)

        if wallet.last_fetched_at is None or wallet.address_type not in AddressType.values:
            fetch_address_service(wallet)

        wallet_context = wallet.get_context()

        context = {
            **wallet_context,
            **base_context,
        }
        logging.info(f"Context for wallet: {context}")

        return HttpResponse(template.render(context, request))


class SearchView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, page_number=1):
        """
        Returns search results.
        """

        template = loader.get_template("search.html")

        query = request.GET.get("query", None)

        if query is None or len(query) == 0:
            return HttpResponseRedirect(reverse("index"))

        base_context = get_base_context()

        objects_per_page = 16

        collections_filterset = search_collections_service(query)
        nfts_filterset = search_nfts_service(query)
        wallets_filterset = search_wallets_service(query)

        collections_paginator = Paginator(collections_filterset, objects_per_page)
        nfts_paginator = Paginator(nfts_filterset, objects_per_page)
        wallets_paginator = Paginator(wallets_filterset, objects_per_page)

        try:
            collection_objects = collections_paginator.page(page_number)
        except EmptyPage:
            collection_objects = []

        try:
            nft_objects = nfts_paginator.page(page_number)
        except EmptyPage:
            # Return empty page if there are no NFTs
            nft_objects = []

        try:
            wallet_objects = wallets_paginator.page(page_number)
        except EmptyPage:
            wallet_objects = []

        # Calculate maximal number of pages
        max_num_pages = max(collections_paginator.num_pages, nfts_paginator.num_pages, wallets_paginator.num_pages)

        logging.info(f"Found {collections_filterset.count()} collections for search query {query}")

        context = {
            **base_context,
            "collections": [collection.get_context() for collection in collection_objects],
            "collections_count": collections_filterset.count(),
            "nfts": [nft.get_context() for nft in nft_objects],
            "nfts_count": nfts_filterset.count(),
            "wallets": [wallet.get_context() for wallet in wallet_objects],
            "wallets_count": wallets_filterset.count(),
            "query": query,
            "page_number": page_number,
            "previous_page_number": page_number - 1 if page_number > 1 else None,
            "next_page_number": page_number + 1 if page_number < max_num_pages else None,
            "num_of_pages": max_num_pages,
        }

        logging.info(f"Context for search: {context}")

        return HttpResponse(template.render(context, request))


class CollectionImageView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, collection_id):
        """
        Returns the collection image.
        """
        collection = get_collection_for_address_service(collection_id)

        try:
            logging.info(f"Collection image: {collection.image}")
            return proxy_image_file_service(collection.image)
        except ValueError:
            return get_default_image_content()


class CollectionCoverView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, collection_id):
        """
        Returns the collection image.
        """
        collection = get_collection_for_address_service(collection_id)

        try:
            return proxy_image_file_service(collection.cover_image, cover=True)
        except ValueError:
            return redirect(f"{SITE_URL}/staticfiles/default_cover.png")


class NFTImageView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, nft_id):
        """
        Returns the NFT image.
        """
        nft = get_nft_for_address_service(nft_id)

        try:
            return proxy_image_file_service(nft.image)
        except ValueError:
            return redirect(f"{SITE_URL}/staticfiles/default_image.png")


class WalletImageView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, wallet_id):
        """
        Returns the wallet icon.
        """
        wallet = get_wallet_for_address_service(wallet_id)

        try:
            return proxy_image_file_service(wallet.icon)
        except ValueError:
            return redirect(f"{SITE_URL}/staticfiles/default_image.png")


class SitemapView(APIView):
    http_method_names = ["get"]

    def get(self, request):
        """
        Return sitemap file response.
        """
        return get_sitemap_handler()


class FaviconView(APIView):
    http_method_names = ["get"]

    def get(self, request):
        """
        Return favicon.
        """
        with open(BASE_DIR / "tonnftscan/static/favicon.ico", "rb") as input_file:
            content = input_file.read()

        return HttpResponse(content, content_type="image/x-icon")
