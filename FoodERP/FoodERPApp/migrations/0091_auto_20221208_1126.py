# Generated by Django 3.0.8 on 2022-12-08 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0090_auto_20221208_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_gsthsncode',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='m_items',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='m_marginmaster',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='m_mrpmaster',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='mc_itemcategorydetails',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='mc_itemgroupdetails',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='t_materialissue',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='t_orders',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='t_workorder',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
