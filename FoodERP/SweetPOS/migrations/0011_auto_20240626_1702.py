# Generated by Django 3.0.8 on 2024-06-26 17:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0010_auto_20240522_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_sposinvoices',
            name='CustomerGSTIN',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='t_sposinvoices',
            name='MobileNo',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='t_sposinvoices',
            name='NetAmount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='t_sposinvoices',
            name='PaymentType',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='t_sposinvoices',
            name='TotalAmount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tc_sposinvoiceitems',
            name='HSNCode',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tc_sposinvoiceitems',
            name='InvoiceDate',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tc_sposinvoiceitems',
            name='Party',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
