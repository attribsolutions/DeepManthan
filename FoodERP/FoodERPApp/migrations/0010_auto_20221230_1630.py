# Generated by Django 3.0.8 on 2022-12-30 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0009_remove_o_batchwiselivestock_grn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='o_batchwiselivestock',
            name='TransactionType',
            field=models.IntegerField(),
        ),
    ]
