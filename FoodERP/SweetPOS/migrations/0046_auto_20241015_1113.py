# Generated by Django 3.0.8 on 2024-10-15 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0045_auto_20241010_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_sweetposmachine',
            name='ServerSequence',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='m_sweetposmachine',
            name='UploadSaleRecordCount',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='m_sweetposmachine',
            name='Validity',
            field=models.DateField(blank=True, null=True),
        ),
    ]
