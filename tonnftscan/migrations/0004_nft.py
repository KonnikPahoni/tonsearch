# Generated by Django 4.0.5 on 2023-12-27 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tonnftscan", "0003_alter_collection_owner"),
    ]

    operations = [
        migrations.CreateModel(
            name="NFT",
            fields=[
                ("address", models.CharField(max_length=255, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=2000)),
                ("description", models.CharField(max_length=10000)),
                ("image", models.CharField(max_length=10000)),
                ("external_url", models.CharField(max_length=10000)),
                ("attributes", models.JSONField()),
                (
                    "collection",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="tonnftscan.collection"
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="tonnftscan.useraddress"
                    ),
                ),
            ],
        ),
    ]
