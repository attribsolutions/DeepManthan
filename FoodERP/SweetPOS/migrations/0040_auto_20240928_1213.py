# Generated by Django 3.0.8 on 2024-09-28 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0039_auto_20240923_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_sweetposmachine',
            name='MachineType',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]