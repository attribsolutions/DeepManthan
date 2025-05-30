# Generated by Django 3.0.8 on 2025-05-31 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0395_m_parties_closingdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='mc_schemeitems',
            name='DiscountType',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mc_schemeitems',
            name='DiscountValue',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mc_schemeitems',
            name='Quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
