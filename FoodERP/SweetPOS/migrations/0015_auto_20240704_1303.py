# Generated by Django 3.0.8 on 2024-07-04 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0014_auto_20240703_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='Amount',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='BaseUnitQuantity',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='BasicAmount',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='CGST',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='CGSTPercentage',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='Discount',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='DiscountAmount',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='GSTAmount',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='GSTPercentage',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='IGST',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='IGSTPercentage',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='Quantity',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='Rate',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='SGST',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
        migrations.AlterField(
            model_name='tc_sposinvoiceitems',
            name='SGSTPercentage',
            field=models.DecimalField(decimal_places=10, max_digits=40),
        ),
    ]
