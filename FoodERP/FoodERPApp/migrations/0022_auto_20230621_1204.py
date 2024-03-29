# Generated by Django 3.0.8 on 2023-06-21 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0021_transactionlog_jsondata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_purchasereturn',
            name='GrandTotal',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='t_purchasereturn',
            name='RoundOffAmount',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='Amount',
            field=models.DecimalField(decimal_places=2, max_digits=30),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='BaseUnitQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=30),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='BasicAmount',
            field=models.DecimalField(decimal_places=2, max_digits=30),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='CGST',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='CGSTPercentage',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='GSTAmount',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='IGST',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='IGSTPercentage',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='MRPValue',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='Quantity',
            field=models.DecimalField(decimal_places=3, max_digits=30),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='Rate',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='SGST',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tc_purchasereturnitems',
            name='SGSTPercentage',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
