from django.urls import path
from django.contrib import admin
from django.views.decorators.cache import cache_page

from tonnftscan.views import (
    IndexView,
    CollectionsView,
    CollectionView,
    NFTView,
    NFTsView,
    WalletView,
    WalletsView,
    SearchView,
    CollectionImageView,
    SitemapView,
    NFTImageView,
    WalletImageView,
    CollectionCoverView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", cache_page(60 * 60 * 4)(IndexView.as_view()), name="index"),
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
    path("collection/<str:collection_id>", cache_page(60 * 60 * 24 * 7)(CollectionView.as_view()), name="collection"),
    path("nfts", NFTsView.as_view(), name="nfts"),
    path("nfts/<int:page_number>", NFTsView.as_view(), name="nfts"),
    path("nft/<str:nft_id>/image", cache_page(60 * 60 * 24 * 7)(NFTImageView.as_view()), name="nft-image"),
    path("nft/<str:nft_id>", cache_page(60 * 60 * 24 * 7)(NFTView.as_view()), name="nft"),
    path("wallets", WalletsView.as_view(), name="wallets"),
    path("wallets/<int:page_number>", WalletsView.as_view(), name="wallets"),
    path("wallet/<str:wallet_id>/image", cache_page(60 * 60 * 24 * 7)(WalletImageView.as_view()), name="wallet-image"),
    path("wallet/<str:wallet_id>", cache_page(60 * 60 * 24 * 7)(WalletView.as_view()), name="wallet"),
    path("search", SearchView.as_view(), name="search"),
    path(
        "sitemap.xml",
        cache_page(60 * 60 * 24)(SitemapView.as_view()),
        name="sitemap",
    ),
]
