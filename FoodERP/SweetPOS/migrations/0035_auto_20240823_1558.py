# Generated by Django 3.0.8 on 2024-08-23 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0034_m_consumermobile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_consumermobile',
            name='Mobile',
            field=models.CharField(max_length=100),
        ),
    ]
