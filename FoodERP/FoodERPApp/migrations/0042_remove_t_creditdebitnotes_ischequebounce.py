# Generated by Django 3.0.8 on 2023-04-08 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0041_auto_20230408_1032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='t_creditdebitnotes',
            name='IsChequeBounce',
        ),
    ]
