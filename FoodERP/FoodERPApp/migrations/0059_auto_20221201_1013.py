# Generated by Django 3.0.8 on 2022-12-01 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0058_o_batchwiselivestock_gst'),
    ]

    operations = [
        migrations.AlterField(
            model_name='o_batchwiselivestock',
            name='GRN',
            field=models.IntegerField(default='Free'),
        ),
    ]
