import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.template import loader
import jwt
import time
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from tonnftscan.models import Collection, NFT, Address
from tonnftscan.services import (
    get_collection_for_address_service,
    get_nft_for_address_service,
    get_wallet_for_address_service,
    search_collections_service,
    search_nfts_service,
    search_wallets_service,
)
from tonnftscan.settings import METABASE_EMBED_KEY, METABASE_SITE_URL
from tonnftscan.utils import get_base_context


class IndexView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request):
        """
        Returns a welcome page for the project.
        """

        template = loader.get_template("index.html")

        payload = {
            "resource": {"dashboard": 3},
            "params": {},
            "exp": round(time.time()) + (60 * 10),  # 10 minute expiration
        }
        token = jwt.encode(payload, METABASE_EMBED_KEY, algorithm="HS256")

        iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"

        context = {
            "iframeUrl": iframeUrl,
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

        collections_filterset = Collection.objects.order_by("-created_at")

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

        template = loader.get_template("nfts.html")
        base_context = get_base_context()

        objects_per_page = 16

        nfts_filterset = NFT.objects.order_by("-created_at")

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

        nfts = [nft.get_context() for nft in objects]

        context = {
            **base_context,
            "nfts": nfts,
            "page_number": page_number,
            "previous_page_number": page_number - 1 if page_number > 1 else None,
            "next_page_number": page_number + 1 if page_number < paginator.num_pages else None,
            "num_of_pages": paginator.num_pages,
            "total_nfts": nfts_filterset.count(),
        }

        return HttpResponse(template.render(context, request))


class WalletsView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, page_number=1):
        """
        Returns the wallet's page.
        """

        template = loader.get_template("wallets.html")
        base_context = get_base_context()

        objects_per_page = 16

        # nfts_owners_list = list(NFT.objects.filter(owner__isnull=False).values_list("owner", flat=True).distinct())
        addresses_filterset = Address.objects.filter(last_fetched_at__isnull=False)

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

        wallets = [wallet.get_context() for wallet in objects]

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

        context = {
            **collection_context,
            **base_context,
            "owner": collection.owner.get_context(),
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

        nft_context = nft.get_context()

        context = {
            **nft_context,
            **base_context,
        }
        logging.info(f"Context for nft: {context}")

        return HttpResponse(template.render(context, request))


class WalletView(APIView):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]

    def get(self, request, wallet_id):
        """
        Returns the page for a wallet.
        """

        template = loader.get_template("wallet.html")

        base_context = get_base_context()
        wallet = get_wallet_for_address_service(wallet_id)

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

    def get(self, request):
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
            collection_objects = collections_paginator.page(1)
        except EmptyPage:
            collection_objects = collections_paginator.page(collections_paginator.num_pages)

        try:
            nft_objects = nfts_paginator.page(1)
        except EmptyPage:
            nft_objects = nfts_paginator.page(nfts_paginator.num_pages)

        try:
            wallet_objects = wallets_paginator.page(1)
        except EmptyPage:
            wallet_objects = wallets_paginator.page(wallets_paginator.num_pages)

        logging.info(f"Found {collections_filterset.count()} collections for search query {query}")

        context = {
            **base_context,
            "collections": [collection.get_context() for collection in collection_objects],
            "collections_count": collections_filterset.count(),
            "nfts": [nft.get_context() for nft in nft_objects],
            "nfts_count": nfts_filterset.count(),
            "wallets": [wallet.get_context() for wallet in wallet_objects],
            "wallets_count": wallets_filterset.count(),
        }
        logging.info(f"Context for search: {context}")

        return HttpResponse(template.render(context, request))
