# Generated by Django 3.0.8 on 2025-02-13 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0337_m_sapposuploadlog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_sapposuploadlog',
            name='FileID',
        ),
        migrations.AddField(
            model_name='m_sapposuploadlog',
            name='File',
            field=models.CharField(default=0, max_length=500),
            preserve_default=False,
        ),
    ]
