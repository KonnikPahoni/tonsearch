# Generated by Django 4.2.8 on 2024-01-11 15:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tonnftscan", "0016_address_address_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="address",
            name="is_wallet",
        ),
    ]
