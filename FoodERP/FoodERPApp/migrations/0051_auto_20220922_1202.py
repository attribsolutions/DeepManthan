# Generated by Django 3.0.8 on 2022-09-22 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0050_m_parties_isdivision'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_pricelist',
            name='MkUpMkDn',
            field=models.BooleanField(default=False),
        ),
    ]
