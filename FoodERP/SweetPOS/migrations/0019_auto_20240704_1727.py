# Generated by Django 3.0.8 on 2024-07-04 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0018_auto_20240704_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t_sposinvoices',
            name='RoundOffAmount',
            field=models.DecimalField(decimal_places=10, max_digits=30),
        ),
    ]
