import logging
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField

from tonnftscan.settings import SITE_URL
from tonnftscan.utils import convert_hex_address_to_user_friendly

User = get_user_model()


class Address(models.Model):
    address = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_scam = models.BooleanField(default=False)
    is_wallet = models.BooleanField(default=False)
    name = models.CharField(max_length=1000, blank=True, null=True, db_index=True)
    last_fetched_at = models.DateTimeField(blank=True, null=True)
    balance = models.BigIntegerField(blank=True, null=True)
    last_activity = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1000, blank=True, null=True)
    interfaces = ArrayField(models.CharField(max_length=1000), default=list)
    icon = models.CharField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return f"{self.address}"

    def get_context(self):
        """
        Returns context for a wallet.
        """

        image = self.icon if self.icon != "" else None

        if image is None:
            image = f"{SITE_URL}/staticfiles/default_image.png"

        nfts_count = NFT.objects.filter(owner=self).count()

        context = {
            "hex_id": self.address,
            "user_friendly_id": convert_hex_address_to_user_friendly(self.address),
            "name": self.name,
            "last_fetched_at": self.last_fetched_at,
            "balance": self.balance,
            "last_activity": self.last_activity,
            "status": self.status,
            "interfaces": self.interfaces,
            "icon": image,
            "is_scam": self.is_scam,
            "is_wallet": self.is_wallet,
            "nfts_count": nfts_count,
        }

        return context


class Collection(models.Model):
    """
    Represents a TON NFT collection.
    """

    address = models.CharField(max_length=255, primary_key=True)
    owner = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=2000, db_index=True)
    description = models.CharField(max_length=10000, db_index=True)
    social_links = ArrayField(models.CharField(max_length=10000))
    marketplace = models.CharField(max_length=1000)
    image = models.CharField(max_length=10000)
    cover_image = models.CharField(max_length=10000)
    external_url = models.CharField(max_length=10000)
    last_fetched_at = models.DateTimeField(blank=True, null=True)
    nfts_count = models.IntegerField(default=0)

    class Meta:
        # Add birthday to the first sublist maybe if it causes problems?
        ordering = ["address"]

    def __str__(self):
        return f"{self.name} ({self.address})"

    def get_nfts_count(self):
        return NFT.objects.filter(collection=self).count()

    def get_context(self):
        """
        Returns context for a collection.
        """

        social_links_prepared = []

        for social_link in self.social_links or []:
            if social_link is None or len(social_link) == 0 or "://" not in social_link:
                logging.info(f"Skipping social link {social_link}")
                continue

            name = social_link.split("://")[1].split("/")[0]

            social_links_prepared.append(
                {
                    "name": name,
                    "url": social_link,
                }
            )

        prepared_description = self.description

        prepared_image = self.image if self.image != "" else None

        if prepared_image is None:
            prepared_image = f"{SITE_URL}/staticfiles/default_image.png"

        context = {
            "hex_id": self.address,
            "user_friendly_id": convert_hex_address_to_user_friendly(self.address),
            "owner_address": convert_hex_address_to_user_friendly(self.owner.address) if self.owner else None,
            "name": self.name,
            "description": prepared_description,
            "social_links": social_links_prepared,
            "marketplace": self.marketplace if self.marketplace != "" else None,
            "image": prepared_image,
            "cover_image": self.cover_image if self.cover_image != "" else None,
            "external_url": self.external_url if self.external_url != "" else None,
            "last_fetched_at": self.last_fetched_at,
            "nfts_count": self.get_nfts_count(),
        }

        return context


class NFT(models.Model):
    """
    Represents a TON NFT.
    """

    address = models.CharField(max_length=255, primary_key=True)
    owner = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True, related_name="nfts")
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, blank=True, null=True, related_name="nfts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=2000, db_index=True)
    description = models.CharField(max_length=10000, db_index=True)
    image = models.CharField(max_length=10000)
    external_url = models.CharField(max_length=10000)
    attributes = models.JSONField()
    sale = models.JSONField(default=dict)
    verified = models.BooleanField(default=False)
    approved_by = models.CharField(max_length=1000, blank=True, null=True)
    last_fetched_at = models.DateTimeField(blank=True, null=True)

    def get_context(self):
        """
        Returns context for a NFT.
        """
        prepared_description = self.description
        prepared_image = self.image if self.image != "" else None

        if prepared_image is None:
            prepared_image = f"{SITE_URL}/staticfiles/default_image.png"

        context = {
            "hex_id": self.address,
            "user_friendly_id": convert_hex_address_to_user_friendly(self.address),
            "collection": self.collection.get_context(),
            "owner_address": convert_hex_address_to_user_friendly(self.owner.address) if self.owner else None,
            "name": self.name,
            "description": prepared_description,
            "image": prepared_image,
            "external_url": self.external_url if self.external_url != "" else None,
            "last_fetched_at": self.last_fetched_at,
            "attributes": self.attributes,
            "sale": self.sale,
            "verified": self.verified,
            "approved_by": self.approved_by,
        }

        return context

    def __str__(self):
        return f"{self.name} ({self.address})"


class Transaction(models.Model):
    """
    Represents a TON NFT transfer.
    """

    transaction_hex = models.CharField(max_length=255, primary_key=True)
    account_address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.IntegerField()


class TransactionAction(models.Model):
    """
    Represents a transaction action.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    type = models.CharField(max_length=1000)
    status = models.CharField(max_length=1000)
    sender_address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True, related_name="actions")
    recipient_address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    nft = models.ForeignKey(NFT, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
