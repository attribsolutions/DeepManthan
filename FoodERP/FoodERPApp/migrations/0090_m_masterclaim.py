# Generated by Django 3.0.8 on 2023-07-28 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0089_auto_20230727_1334'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_MasterClaim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FromDate', models.DateField()),
                ('ToDate', models.DateField()),
                ('PrimaryAmount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('SecondaryAmount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('ReturnAmount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('NetSaleValue', models.DecimalField(decimal_places=2, max_digits=20)),
                ('Budget', models.DecimalField(decimal_places=2, max_digits=20)),
                ('ClaimAmount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('ClaimAgainstNetSale', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
            options={
                'db_table': 'M_MasterClaim',
            },
        ),
    ]
