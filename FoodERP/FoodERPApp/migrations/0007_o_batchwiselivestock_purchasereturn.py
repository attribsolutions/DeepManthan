# Generated by Django 3.0.8 on 2023-05-11 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0006_auto_20230511_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='o_batchwiselivestock',
            name='PurchaseReturn',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='BatchWiseLiveStockPurchasereturnID', to='FoodERPApp.T_PurchaseReturn'),
        ),
    ]
