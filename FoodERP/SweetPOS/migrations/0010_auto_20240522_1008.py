# Generated by Django 3.0.8 on 2024-05-22 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0009_o_sposdatewiselivestock_t_sposstock_t_sposstockout'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='BaseUnitQuantity',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='BatchCode',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='BatchCodeID',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='Difference',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='IsDeleted',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='IsSaleable',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='IsStockAdjustment',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='MRP',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='MRPValue',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='Quantity',
        ),
        migrations.RemoveField(
            model_name='t_sposstockout',
            name='Unit',
        ),
    ]
