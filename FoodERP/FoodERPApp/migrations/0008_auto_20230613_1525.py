# Generated by Django 3.0.8 on 2023-06-13 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0007_auto_20230613_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_orderitems',
            name='QtyInBox',
            field=models.DecimalField(decimal_places=20, max_digits=30),
        ),
        migrations.AlterField(
            model_name='tc_orderitems',
            name='QtyInKg',
            field=models.DecimalField(decimal_places=20, max_digits=30),
        ),
        migrations.AlterField(
            model_name='tc_orderitems',
            name='QtyInNo',
            field=models.DecimalField(decimal_places=20, max_digits=30),
        ),
    ]
