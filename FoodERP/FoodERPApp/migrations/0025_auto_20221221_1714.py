# Generated by Django 3.0.8 on 2022-12-21 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0024_auto_20221221_1713'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_drivers',
            name='CreatedBy',
        ),
        migrations.RemoveField(
            model_name='m_drivers',
            name='CreatedOn',
        ),
        migrations.RemoveField(
            model_name='m_drivers',
            name='UpdatedBy',
        ),
        migrations.RemoveField(
            model_name='m_drivers',
            name='UpdatedOn',
        ),
    ]
