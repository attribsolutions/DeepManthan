# Generated by Django 3.0.8 on 2024-03-21 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0264_auto_20240305_1333'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tc_grnreferences',
            unique_together={('Invoice',)},
        ),
    ]