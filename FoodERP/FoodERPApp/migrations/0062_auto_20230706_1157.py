# Generated by Django 3.0.8 on 2023-07-06 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0061_auto_20230705_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_loadingsheet',
            name='Route',
            field=models.CharField(max_length=500),
        ),
    ]
