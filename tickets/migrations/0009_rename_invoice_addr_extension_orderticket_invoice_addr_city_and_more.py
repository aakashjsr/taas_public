# Generated by Django 4.1.4 on 2023-03-05 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0008_rename_market_requestticket_market_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orderticket",
            old_name="invoice_addr_extension",
            new_name="invoice_addr_city",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="invoice_addr_street_and_house_number",
            new_name="invoice_addr_line_1",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="invoice_addr_zipcode_and_city",
            new_name="invoice_addr_line_2",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="shipping_addr_extension",
            new_name="invoice_addr_line_3",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="shipping_addr_street_and_house_number",
            new_name="invoice_addr_zipcode",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="shipping_addr_zipcode_and_city",
            new_name="shipping_addr_city",
        ),
        migrations.AddField(
            model_name="orderticket",
            name="shipping_addr_line_1",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="shipping_addr_line_2",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="shipping_addr_line_3",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="shipping_addr_zipcode",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]