# Generated by Django 3.0.8 on 2022-12-21 16:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0022_auto_20221221_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_termsandconditions',
            name='CreatedBy',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='m_termsandconditions',
            name='CreatedOn',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='m_termsandconditions',
            name='UpdatedBy',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='m_termsandconditions',
            name='UpdatedOn',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
