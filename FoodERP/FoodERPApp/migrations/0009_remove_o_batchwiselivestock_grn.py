# Generated by Django 3.0.8 on 2022-12-30 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0008_o_batchwiselivestock_grn'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='GRN',
        ),
    ]
