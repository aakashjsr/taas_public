# Generated by Django 4.1.4 on 2023-03-05 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0011_orderticket_dhl_shipping_label_number_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orderticket",
            old_name="dhl_shipping_label_url",
            new_name="dhl_shipping_label_data",
        ),
    ]
