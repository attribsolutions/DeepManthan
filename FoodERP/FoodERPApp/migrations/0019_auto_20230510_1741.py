# Generated by Django 3.0.8 on 2023-05-10 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0018_auto_20230510_1726'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_bank',
            name='Company',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='PurchaseReturn',
        ),
    ]
