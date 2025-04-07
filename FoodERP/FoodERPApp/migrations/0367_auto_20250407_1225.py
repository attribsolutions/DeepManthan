# Generated by Django 3.0.8 on 2025-04-07 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0366_auto_20250404_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='o_datewiselivestock',
            name='IBPurchase',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='o_datewiselivestock',
            name='IBSale',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=20),
            preserve_default=False,
        ),
    ]
