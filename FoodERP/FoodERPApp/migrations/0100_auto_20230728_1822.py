# Generated by Django 3.0.8 on 2023-07-28 18:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0099_auto_20230728_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_masterclaim',
            name='CreatedBy',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='m_masterclaim',
            name='CreatedOn',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
