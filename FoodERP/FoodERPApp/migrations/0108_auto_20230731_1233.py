# Generated by Django 3.0.8 on 2023-07-31 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0107_remove_tc_purchasereturnitemimages_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_purchasereturnitemimages',
            name='Item_pic',
            field=models.TextField(blank=True, null=True),
        ),
    ]
