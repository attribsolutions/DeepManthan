# Generated by Django 3.0.8 on 2023-06-22 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0028_m_partysettingsdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mc_settingsdetails',
            name='Party',
        ),
    ]
