# Generated by Django 3.0.8 on 2024-09-05 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0307_m_users_posratetype'),
    ]

    operations = [
        migrations.CreateModel(
            name='debug_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debug_message', models.CharField(max_length=300, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'debug_log',
            },
        ),
    ]
