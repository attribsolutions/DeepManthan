# Generated by Django 3.0.8 on 2023-07-31 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0106_remove_t_stock_livebatche'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tc_purchasereturnitemimages',
            name='Image',
        ),
    ]
