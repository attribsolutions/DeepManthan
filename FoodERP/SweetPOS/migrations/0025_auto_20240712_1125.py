# Generated by Django 3.0.8 on 2024-07-12 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0024_auto_20240711_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_sposinvoices',
            name='Description',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='t_sposinvoices',
            name='IsDeleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='t_sposinvoices',
            name='ReferenceInvoiceID',
            field=models.IntegerField(null=True),
        ),
    ]
