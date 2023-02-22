# Generated by Django 3.0.8 on 2023-02-22 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0106_auto_20230220_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_challanitems',
            name='Amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='BasicAmount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='BatchCode',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='CGST',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='CGSTPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='Discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='DiscountAmount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='GST',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ChallanItemGST', to='FoodERPApp.M_GSTHSNCode'),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='GSTAmount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='IGST',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='IGSTPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='Item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='FoodERPApp.M_Items'),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='Quantity',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='Rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='SGST',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='SGSTPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='TaxType',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tc_challanitems',
            name='Unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ChallanUnitID', to='FoodERPApp.MC_ItemUnits'),
        ),
    ]
