# Generated by Django 4.2.8 on 2024-02-11 20:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("indicators", "0005_collectionindicators_burn_ratio_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="collectionindicators",
            old_name="spam_ratio",
            new_name="spam_factor",
        ),
        migrations.RenameField(
            model_name="collectionindicatorspercentiles",
            old_name="spam_ratio",
            new_name="spam_factor",
        ),
    ]
