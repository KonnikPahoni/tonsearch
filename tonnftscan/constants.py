from django.db import models

# List of collections for which no rel=nofollow is added on NFT and collection links.

REL_NOFOLLOW_EXCEPTIONS = [
    "EQAAvO8rqkV6X4HqOtq1VHHT4_NGlhahJYimHBAg97NvlL8I",
    "EQB5-7Vts5Pfu0csjH_g0l4ewMW2yIVZjQlKOVMQUDhs9MK_",
    "EQDznivJJ5MVc89Jk4iYtEzSRi_FD-0R6urzhScKBchkZdBC",
]


class AddressType(models.TextChoices):
    WALLET = "wallet", "Wallet"
    NFT_SALE = "nft_sale", "NFT Sale"


NULL_ADDRESSES_LIST = [
    "EQAREREREREREREREREREREREREREREREREREREREREREeYT",
    "EQD__________________________________________0vo",
    "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c",
]
