# Generated by Django 3.0.8 on 2025-02-04 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0334_auto_20250203_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_grnitems',
            name='DiscrepancyComment',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
