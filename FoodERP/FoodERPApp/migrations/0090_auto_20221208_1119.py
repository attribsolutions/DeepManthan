# Generated by Django 3.0.8 on 2022-12-08 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0089_tc_materialissueworkorders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_category',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='m_categorytype',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='m_group',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='m_grouptype',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='m_imagetypes',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='mc_subgroup',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
