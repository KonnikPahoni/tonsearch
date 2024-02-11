from django.db import models

from tonnftscan.models import Collection


class CollectionIndicators(models.Model):
    """
    Represents a collection search.
    """

    collection = models.OneToOneField(Collection, on_delete=models.CASCADE, related_name="collection_search")
    google_impressions_total = models.IntegerField(default=0, help_text="Number of impressions in Google")
    google_impressions_last_30_days = models.IntegerField(
        default=0, help_text="Number of impressions in Google for the last 30 days"
    )
    google_clicks_total = models.IntegerField(default=0, help_text="Number of clicks in Google")
    google_clicks_last_30_days = models.IntegerField(
        default=0, help_text="Number of clicks in Google for the last 30 days"
    )
    google_clicks_last_7_days = models.IntegerField(
        default=0, help_text="Number of clicks in Google for the last 7 days"
    )
    google_ctr_total = models.FloatField(default=0, help_text="CTR in Google")
    google_ctr_last_30_days = models.FloatField(default=0, help_text="CTR in Google for the last 30 days")
    google_position_total = models.FloatField(default=0, help_text="Position in Google")
    google_position_last_30_days = models.FloatField(default=0, help_text="Position in Google for the last 30 days")
    spam_ratio = models.FloatField(default=0, help_text="Spam ratio")


class DailyIndicator(models.Model):
    """
    Represents a daily indicator.
    """

    date = models.DateField(primary_key=True)
    collections_count = models.IntegerField()
    collection_nfts_count = models.IntegerField()
    nft_holders_count = models.IntegerField()
    nfts_on_sale_count = models.IntegerField()

    def __str__(self):
        return f"{self.date}: {self.collections_count} collections, {self.collection_nfts_count} collection NFTs, {self.nft_holders_count} NFT holders, {self.nfts_on_sale_count} NFTs on sale"
