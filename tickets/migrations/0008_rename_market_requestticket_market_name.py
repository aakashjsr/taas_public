# Generated by Django 4.1.4 on 2023-03-05 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0007_requestticket_market"),
    ]

    operations = [
        migrations.RenameField(
            model_name="requestticket",
            old_name="market",
            new_name="market_name",
        ),
    ]
