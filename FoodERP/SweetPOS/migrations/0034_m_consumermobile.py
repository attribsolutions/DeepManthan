# Generated by Django 3.0.8 on 2024-08-23 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0033_m_sposratemaster_isdeleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_ConsumerMobile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Mobile', models.IntegerField()),
                ('IsLinkToBill', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'M_ConsumerMobile',
            },
        ),
    ]
