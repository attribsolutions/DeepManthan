# Generated by Django 3.0.8 on 2025-04-09 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0371_o_datewiselivestock_materialissue'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_pages',
            name='Is_New',
            field=models.BooleanField(default=False),
        ),
    ]
