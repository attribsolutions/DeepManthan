# Generated by Django 3.0.8 on 2024-08-06 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0032_auto_20240802_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_sposratemaster',
            name='IsDeleted',
            field=models.BooleanField(default=False),
        ),
    ]
