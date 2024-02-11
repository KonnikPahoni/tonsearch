from django.db import models

from tonnftscan.models import Collection


class CollectionIndicators(models.Model):
    """
    Stores indicators for a collection.
    """

    collection = models.OneToOneField(Collection, on_delete=models.CASCADE, related_name="collection_indicators")
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
    burn_ratio = models.FloatField(
        default=None, help_text="Burned NFTs / total NFTs in the collection", blank=True, null=True
    )
    spam_factor = models.FloatField(
        default=None, help_text="Number of NFTs from collection burned by different users", blank=True, null=True
    )
    spread_ratio_current = models.FloatField(
        default=None,
        help_text="Spread ratio: number of wallets with NFTs from collection / total number of NFTs",
        blank=True,
        null=True,
    )
    spread_historical = models.FloatField(
        default=None, help_text="Number of wallets who owned NFTs over time", blank=True, null=True
    )


class CollectionIndicatorsPercentiles(models.Model):
    """
    Stores percentiles for collection indicators.
    """

    collection = models.OneToOneField(
        Collection, on_delete=models.CASCADE, related_name="collection_indicators_percentiles"
    )
    burn_ratio = models.FloatField(default=None, help_text="Burn ratio percentile", blank=True, null=True)
    spam_factor = models.FloatField(default=None, help_text="Spam ratio percentile", blank=True, null=True)
    spread_ratio_current = models.FloatField(default=None, help_text="Spread ratio percentile", blank=True, null=True)


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
