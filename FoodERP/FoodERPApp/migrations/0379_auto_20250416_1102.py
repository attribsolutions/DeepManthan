# Generated by Django 3.0.8 on 2025-04-16 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0378_auto_20250414_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_items',
            name='ItemCode',
            field=models.IntegerField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='m_parties',
            name='ShortName',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='t_voucher',
            name='Amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
    ]
