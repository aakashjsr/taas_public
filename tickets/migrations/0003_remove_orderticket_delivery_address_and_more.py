# Generated by Django 4.1.4 on 2023-02-23 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets", "0002_orderedproduct"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderticket",
            name="delivery_address",
        ),
        migrations.RemoveField(
            model_name="orderticket",
            name="invoice_address",
        ),
        migrations.AddField(
            model_name="orderticket",
            name="invoice_addr_city",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="invoice_addr_company_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="invoice_addr_first_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="invoice_addr_last_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="invoice_addr_line_1",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="invoice_addr_line_2",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="invoice_addr_line_3",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="invoice_addr_zipcode",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="shipping_addr_city",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="shipping_addr_company_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="shipping_addr_first_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="orderticket",
            name="shipping_addr_last_name",
            field=models.CharField(blank=True, max_length=200, null=True),
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
