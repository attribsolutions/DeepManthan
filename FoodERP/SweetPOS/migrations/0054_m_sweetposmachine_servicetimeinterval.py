# Generated by Django 3.0.8 on 2024-12-04 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0053_auto_20241204_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_sweetposmachine',
            name='ServiceTimeInterval',
            field=models.TimeField(blank=True, null=True),
        ),
    ]