# Generated by Django 4.0.5 on 2023-12-27 18:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tonnftscan", "0005_collection_last_fetched_at_nft_approved_by_nft_sale_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nft",
            name="sale",
            field=models.JSONField(default=dict),
        ),
    ]
