# Generated by Django 3.0.8 on 2023-03-10 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0031_remove_m_partytype_isretailer'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_partytype',
            name='IsRetailer',
            field=models.BooleanField(default=False),
        ),
    ]
