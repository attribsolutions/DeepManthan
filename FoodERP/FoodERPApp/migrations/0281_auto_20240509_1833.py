# Generated by Django 3.0.8 on 2024-05-09 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0280_m_ratemaster_pricelist'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_materialissue',
            name='Status',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='t_workorder',
            name='Status',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]