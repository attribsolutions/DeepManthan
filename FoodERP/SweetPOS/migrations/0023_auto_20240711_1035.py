# Generated by Django 3.0.8 on 2024-07-11 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0022_auto_20240708_1727'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='t_sposinvoices',
            name='DeletedFromSAP',
        ),
        migrations.RemoveField(
            model_name='t_sposinvoices',
            name='ImportFromExcel',
        ),
    ]
