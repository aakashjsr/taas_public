# Generated by Django 4.1.4 on 2023-03-05 11:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0005_alter_orderticket_invoice_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orderticket",
            old_name="invoice_addr_city",
            new_name="invoice_addr_extension",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="invoice_addr_line_1",
            new_name="invoice_addr_street_and_house_number",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="invoice_addr_line_2",
            new_name="invoice_addr_zipcode_and_city",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="invoice_addr_line_3",
            new_name="shipping_addr_extension",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="invoice_addr_zipcode",
            new_name="shipping_addr_street_and_house_number",
        ),
        migrations.RenameField(
            model_name="orderticket",
            old_name="shipping_addr_city",
            new_name="shipping_addr_zipcode_and_city",
        ),
        migrations.RemoveField(
            model_name="orderticket",
            name="shipping_addr_line_1",
        ),
        migrations.RemoveField(
            model_name="orderticket",
            name="shipping_addr_line_2",
        ),
        migrations.RemoveField(
            model_name="orderticket",
            name="shipping_addr_line_3",
        ),
        migrations.RemoveField(
            model_name="orderticket",
            name="shipping_addr_zipcode",
        ),
    ]
