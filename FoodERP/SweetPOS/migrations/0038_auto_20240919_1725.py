# Generated by Django 3.0.8 on 2024-09-19 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0037_m_sweetposmachine'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_sweetposmachine',
            name='ClientID',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='m_sweetposmachine',
            name='MachineRole',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
