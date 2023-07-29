# Generated by Django 3.0.8 on 2023-07-29 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0101_thirdpartyapitransactionlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='MC_ReturnReasonwiseMasterClaim',
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
                ('ItemReason', models.IntegerField()),
                ('PartyType', models.IntegerField()),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ClaimmParty', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'MC_ReturnReasonwiseMasterClaim',
            },
        ),
    ]
