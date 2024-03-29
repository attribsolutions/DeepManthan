# Generated by Django 3.0.8 on 2023-07-24 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0084_auto_20230722_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='Discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='DiscountAmount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='DiscountType',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
