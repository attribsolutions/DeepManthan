# Generated by Django 3.0.8 on 2023-08-19 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0132_m_items_budget'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedAmount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedBasicAmount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedCGST',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedCGSTPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedGSTAmount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedGSTPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedIGST',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedIGSTPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedRate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedSGST',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='tc_purchasereturnitems',
            name='ApprovedSGSTPercentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
