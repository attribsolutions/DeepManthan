# Generated by Django 3.0.8 on 2025-02-27 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0340_auto_20250214_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_grnitems',
            name='DiscrepancyReason',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
