# Generated by Django 3.0.8 on 2023-09-07 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0159_t_creditdebitnotes_isdeleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_purchasereturnitemimages',
            name='Image',
            field=models.ImageField(blank=True, default='', null=True, upload_to='Images\\ReturnImages'),
        ),
    ]
