# Generated by Django 3.0.8 on 2023-06-19 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0015_auto_20230617_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_invoiceitems',
            name='BaseUnitQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=20),
        ),
    ]
