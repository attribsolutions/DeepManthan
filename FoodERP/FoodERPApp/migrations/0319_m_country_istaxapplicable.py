# Generated by Django 3.0.8 on 2024-10-18 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0318_m_parties_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_country',
            name='IsTaxApplicable',
            field=models.BooleanField(default=False),
        ),
    ]
