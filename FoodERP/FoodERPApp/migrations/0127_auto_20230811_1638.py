# Generated by Django 3.0.8 on 2023-08-11 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0126_auto_20230811_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='ApprovedByCompany',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
