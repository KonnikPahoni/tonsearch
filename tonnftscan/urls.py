from django.urls import path, re_path
from django.contrib import admin
from django.views.decorators.cache import cache_page

from tonnftscan.views import (
    IndexView,
    CollectionsView,
    CollectionView,
    NFTView,
    NFTsView,
    AddressView,
    AddressesView,
    SearchView,
    CollectionImageView,
    SitemapView,
    NFTImageView,
    WalletImageView,
    CollectionCoverView,
    favicon_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", cache_page(60 * 60 * 12)(IndexView.as_view()), name="index"),
    path("collections", CollectionsView.as_view(), name="collections"),
    path("collections/<int:page_number>", CollectionsView.as_view(), name="collections"),
    path(
        "collection/<str:collection_id>/image",
        cache_page(60 * 60 * 24 * 7)(CollectionImageView.as_view()),
        name="collection-image",
    ),
    path(
        "collection/<str:collection_id>/cover",
        cache_page(60 * 60 * 24 * 7)(CollectionCoverView.as_view()),
        name="collection-cover",
    ),
    path("collection/<str:collection_id>", cache_page(60 * 60 * 24)(CollectionView.as_view()), name="collection"),
    path("nfts", NFTsView.as_view(), name="nfts"),
    path("nfts/<int:page_number>", NFTsView.as_view(), name="nfts"),
    path("nft/<str:nft_id>/image", cache_page(60 * 60 * 24 * 7)(NFTImageView.as_view()), name="nft-image"),
    path("nft/<str:nft_id>", cache_page(60 * 60 * 24)(NFTView.as_view()), name="nft"),
    path("addresses", AddressesView.as_view(), name="wallets"),
    path("addresses/<int:page_number>", AddressesView.as_view(), name="wallets"),
    path("address/<str:wallet_id>/image", cache_page(60 * 60 * 24 * 7)(WalletImageView.as_view()), name="wallet-image"),
    path("address/<str:wallet_id>", cache_page(60 * 60 * 24)(AddressView.as_view()), name="wallet"),
    path("search", SearchView.as_view(), name="search"),
    path(
        "sitemap.xml",
        cache_page(60 * 60 * 24)(SitemapView.as_view()),
        name="sitemap",
    ),
    re_path(r"^favicon\.ico$", favicon_view),
]
