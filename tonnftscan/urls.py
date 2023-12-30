from django.urls import path
from django.contrib import admin

from tonnftscan.views import (
    IndexView,
    CollectionsView,
    CollectionView,
    NFTView,
    NFTsView,
    WalletView,
    WalletsView,
    SearchView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("collections", CollectionsView.as_view(), name="collections"),
    path("collections/<int:page_number>", CollectionsView.as_view(), name="collections"),
    path("collection/<str:collection_id>", CollectionView.as_view(), name="collection"),
    path("nfts", NFTsView.as_view(), name="nfts"),
    path("nfts/<int:page_number>", NFTsView.as_view(), name="nfts"),
    path("nft/<str:nft_id>", NFTView.as_view(), name="nft"),
    path("wallets", WalletsView.as_view(), name="wallets"),
    path("wallets/<int:page_number>", WalletsView.as_view(), name="wallets"),
    path("wallet/<str:wallet_id>", WalletView.as_view(), name="wallet"),
    path("search", SearchView.as_view(), name="search"),
]
