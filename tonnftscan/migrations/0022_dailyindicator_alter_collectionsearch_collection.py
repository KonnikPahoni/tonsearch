# Generated by Django 4.2.8 on 2024-01-22 21:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tonnftscan", "0021_address_num_of_nft_transactions"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyIndicator",
            fields=[
                ("date", models.DateField(primary_key=True, serialize=False)),
                ("collections_count", models.IntegerField()),
                ("collection_nfts_count", models.IntegerField()),
                ("nft_holders_count", models.IntegerField()),
                ("nfts_on_sale_count", models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name="collectionsearch",
            name="collection",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collection_search",
                to="tonnftscan.collection",
            ),
        ),
    ]