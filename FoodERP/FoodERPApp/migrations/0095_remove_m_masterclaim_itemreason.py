# Generated by Django 3.0.8 on 2023-07-28 16:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0094_m_masterclaim_itemreason'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_masterclaim',
            name='ItemReason',
        ),
    ]
