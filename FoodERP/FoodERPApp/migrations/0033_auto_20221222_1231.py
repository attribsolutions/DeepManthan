# Generated by Django 3.0.8 on 2022-12-22 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0032_auto_20221222_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_production',
            name='ActualQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='t_production',
            name='EstimatedQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
    ]
