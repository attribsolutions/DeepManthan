# Generated by Django 3.0.8 on 2022-12-29 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mc_itemunits',
            name='BaseUnitQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
    ]
