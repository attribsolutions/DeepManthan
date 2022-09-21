# Generated by Django 3.0.8 on 2022-09-21 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0048_delete_mc_partyaddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='MC_PartyAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Address', models.CharField(max_length=500)),
                ('FSSAINo', models.CharField(max_length=500)),
                ('FSSAIExipry', models.DateField(blank=True)),
                ('PIN', models.CharField(max_length=500)),
                ('IsDefault', models.BooleanField(default=False)),
                ('AddressType', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='AddressType', to='FoodERPApp.M_AddressTypes')),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PartyAddress', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'MC_PartyAddress',
            },
        ),
    ]
