# Generated by Django 3.0.8 on 2023-11-21 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0218_auto_20231107_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_claimtrackingentry',
            name='Remark',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]