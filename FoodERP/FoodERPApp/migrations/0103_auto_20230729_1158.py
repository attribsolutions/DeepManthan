# Generated by Django 3.0.8 on 2023-07-29 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0102_auto_20230729_1143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='t_stock',
            old_name='BaseunitQuantity',
            new_name='BaseUnitQuantity',
        ),
    ]
