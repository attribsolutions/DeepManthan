# Generated by Django 3.0.8 on 2024-05-17 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0284_auto_20240516_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_items',
            name='SAPItemCode',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]