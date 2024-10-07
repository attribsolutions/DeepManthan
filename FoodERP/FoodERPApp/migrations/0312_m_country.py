# Generated by Django 3.0.8 on 2024-10-03 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0311_debug_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Country', models.CharField(max_length=500)),
                ('Currency', models.CharField(max_length=500)),
                ('CurrencySymbol', models.CharField(max_length=500)),
                ('Weight', models.CharField(max_length=500)),
            ],
            options={
                'db_table': 'M_Country',
            },
        ),
    ]