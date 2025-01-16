# Generated by Django 3.0.8 on 2025-01-15 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0330_auto_20250115_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_giftvouchercode',
            name='InvoiceAmount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='m_giftvouchercode',
            name='InvoiceDate',
            field=models.DateField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='m_giftvouchercode',
            name='InvoiceNumber',
            field=models.CharField(default=0, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='m_giftvouchercode',
            name='Party',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='m_giftvouchercode',
            name='client',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]