# Generated by Django 4.2.8 on 2024-01-21 21:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tonnftscan", "0020_collectionsearch"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="num_of_nft_transactions",
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
