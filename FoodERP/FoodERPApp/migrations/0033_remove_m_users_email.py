# Generated by Django 3.0.8 on 2022-07-05 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0032_auto_20220705_1241'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_users',
            name='email',
        ),
    ]
