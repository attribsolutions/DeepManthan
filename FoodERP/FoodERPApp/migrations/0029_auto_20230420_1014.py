# Generated by Django 3.0.8 on 2023-04-20 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0028_auto_20230420_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_purchasereturnitemimages',
            name='PurchaseReturnItem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ReturnItemImages', to='FoodERPApp.TC_PurchaseReturnItems'),
        ),
    ]
