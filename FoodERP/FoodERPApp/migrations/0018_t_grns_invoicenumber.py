# Generated by Django 3.0.8 on 2023-01-06 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0017_auto_20230106_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_grns',
            name='InvoiceNumber',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
    ]
