# Generated by Django 3.0.8 on 2023-12-23 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0246_auto_20231211_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_items',
            name='IsFranchisesItem',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='m_partytype',
            name='IsFranchises',
            field=models.BooleanField(default=False),
        ),
    ]