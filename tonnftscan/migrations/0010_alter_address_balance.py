# Generated by Django 4.0.5 on 2023-12-28 23:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tonnftscan", "0009_remove_nft_transactions_fetched_at_address_balance_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="balance",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
