# Generated by Django 3.0.8 on 2023-07-18 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0068_tc_purchasereturnreferences_subreturn'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_purchasereturn',
            name='IsApproved',
            field=models.BooleanField(default=False),
        ),
    ]
