# Generated by Django 3.0.8 on 2024-05-16 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0283_auto_20240514_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_materialissue',
            name='RemainNumberOfLot',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='t_materialissue',
            name='RemaninLotQuantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='t_workorder',
            name='RemainNumberOfLot',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='t_workorder',
            name='RemaninQuantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=15),
            preserve_default=False,
        ),
    ]
