# Generated by Django 3.0.8 on 2024-08-31 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0035_auto_20240823_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_consumermobile',
            name='MacID',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
