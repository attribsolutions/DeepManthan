# Generated by Django 3.0.8 on 2022-12-16 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0007_auto_20221216_1044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='t_materialissue',
            name='IsReIssueID',
        ),
        migrations.RemoveField(
            model_name='t_materialissue',
            name='ReIssueID',
        ),
        migrations.RemoveField(
            model_name='t_materialissue',
            name='Status',
        ),
    ]
