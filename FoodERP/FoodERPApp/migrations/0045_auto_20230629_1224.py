# Generated by Django 3.0.8 on 2023-06-29 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0044_auto_20230628_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_grnitems',
            name='MRPValue',
            field=models.IntegerField(),
        ),
    ]
