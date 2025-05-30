# Generated by Django 3.0.8 on 2025-03-13 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0346_mc_schemeitems'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_scheme',
            name='Message',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='m_scheme',
            name='OverLappingScheme',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='m_scheme',
            name='SchemeDetails',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='tc_grnitems',
            name='AccountingQuantity',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=20, null=True),
        ),
    ]
