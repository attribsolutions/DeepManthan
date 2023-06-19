# Generated by Django 3.0.8 on 2023-06-17 16:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0012_auto_20230617_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_grnitems',
            name='BaseUnitQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=20, validators=[django.core.validators.MaxValueValidator(9999999999.999), django.core.validators.MinValueValidator(-9999999999.999)]),
        ),
    ]
