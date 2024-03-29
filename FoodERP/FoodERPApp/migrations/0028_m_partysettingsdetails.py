# Generated by Django 3.0.8 on 2023-06-22 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0027_auto_20230621_1713'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_PartySettingsDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Value', models.CharField(max_length=500)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='SetCompany', to='FoodERPApp.C_Companies')),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='SetParty', to='FoodERPApp.M_Parties')),
                ('Setting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Settingid', to='FoodERPApp.M_Settings')),
            ],
            options={
                'db_table': 'M_PartySettingsDetails',
            },
        ),
    ]
