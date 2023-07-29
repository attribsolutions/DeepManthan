# Generated by Django 3.0.8 on 2023-07-29 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0100_auto_20230728_1822'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThirdPartyAPITransactionlog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TranasactionDate', models.DateField()),
                ('Transactiontime', models.DateTimeField(auto_now_add=True)),
                ('User', models.IntegerField()),
                ('IPaddress', models.CharField(max_length=500)),
                ('PartyID', models.IntegerField()),
                ('TransactionDetails', models.CharField(max_length=500)),
                ('JsonData', models.TextField(blank=True)),
                ('ThirdParytSource', models.CharField(max_length=500)),
            ],
            options={
                'db_table': 'ThirdPartyAPITransactionlog',
            },
        ),
    ]
