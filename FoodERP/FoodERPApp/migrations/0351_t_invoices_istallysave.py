# Generated by Django 3.0.8 on 2025-03-21 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0350_auto_20250321_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_invoices',
            name='IsTallySave',
            field=models.BooleanField(default=False),
        ),
    ]
