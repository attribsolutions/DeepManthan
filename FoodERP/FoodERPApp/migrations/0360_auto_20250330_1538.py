# Generated by Django 3.0.8 on 2025-03-30 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0359_tc_invoiceitems_trayquantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_invoiceitems',
            name='TrayQuantity',
            field=models.DecimalField(blank=True, decimal_places=20, max_digits=30, null=True),
        ),
    ]
