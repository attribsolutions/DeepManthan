# Generated by Django 3.0.8 on 2023-10-23 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0196_m_centralserviceitems_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_centralserviceitems',
            name='Company',
        ),
    ]
