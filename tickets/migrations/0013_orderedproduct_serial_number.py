# Generated by Django 4.1.4 on 2023-03-11 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "tickets",
            "0012_rename_dhl_shipping_label_url_orderticket_dhl_shipping_label_data",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="orderedproduct",
            name="serial_number",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]