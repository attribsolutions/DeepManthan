# Generated by Django 3.0.8 on 2025-01-31 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0332_auto_20250116_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_grns',
            name='IsSave',
            field=models.BooleanField(default=False),
        ),
    ]
