# Generated by Django 3.0.8 on 2023-05-11 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_receipts',
            name='Customer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='ReceiptCustomer', to='FoodERPApp.M_Parties'),
            preserve_default=False,
        ),
    ]
