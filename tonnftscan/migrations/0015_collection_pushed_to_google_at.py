# Generated by Django 4.2.8 on 2024-01-02 15:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tonnftscan", "0014_collection_nfts_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="collection",
            name="pushed_to_google_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]