# Generated by Django 3.0.8 on 2024-04-11 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0274_m_ratemaster'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_ratemaster',
            name='Company',
        ),
    ]
