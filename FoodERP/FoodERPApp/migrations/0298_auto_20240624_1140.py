# Generated by Django 3.0.8 on 2024-06-24 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0297_auto_20240624_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_items',
            name='SAPItemCode',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
