# Generated by Django 3.0.8 on 2023-10-17 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0183_m_partysettingsdetails_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_items',
            name='SkyggeProductID',
            field=models.IntegerField(default=False),
        ),
    ]
