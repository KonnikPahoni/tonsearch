# Generated by Django 4.2.8 on 2024-01-02 12:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tonnftscan", "0011_alter_address_name_alter_collection_description_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="collection",
            options={"ordering": ["address"]},
        ),
    ]