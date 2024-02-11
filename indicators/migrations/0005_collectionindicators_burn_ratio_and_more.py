# Generated by Django 4.2.8 on 2024-02-11 20:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("indicators", "0004_collectionindicators_spread_historical"),
    ]

    operations = [
        migrations.AddField(
            model_name="collectionindicators",
            name="burn_ratio",
            field=models.FloatField(
                blank=True, default=None, help_text="Burned NFTs / total NFTs in the collection", null=True
            ),
        ),
        migrations.AddField(
            model_name="collectionindicatorspercentiles",
            name="burn_ratio",
            field=models.FloatField(blank=True, default=None, help_text="Burn ratio percentile", null=True),
        ),
        migrations.AlterField(
            model_name="collectionindicators",
            name="spam_ratio",
            field=models.FloatField(
                blank=True,
                default=None,
                help_text="Number of NFTs from collection burned by different users",
                null=True,
            ),
        ),
    ]
