# Generated by Django 3.0.8 on 2023-05-06 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_invoiceitems',
            name='GSTValue',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
    ]
