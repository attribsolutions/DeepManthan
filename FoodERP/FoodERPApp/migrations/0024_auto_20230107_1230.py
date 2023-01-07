# Generated by Django 3.0.8 on 2023-01-07 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0023_mc_partyprefixs_workorderprefix'),
    ]

    operations = [
        migrations.AddField(
            model_name='mc_partyprefixs',
            name='MaterialIssueprefix',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='t_materialissue',
            name='FullMaterialIssueNumber',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='t_materialissue',
            name='MaterialIssueNumber',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
