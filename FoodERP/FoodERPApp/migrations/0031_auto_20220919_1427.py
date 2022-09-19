# Generated by Django 3.0.8 on 2022-09-19 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0030_m_parties_partytype'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_PriceList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_PriceList',
            },
        ),
        migrations.RemoveField(
            model_name='m_partytype',
            name='DivisionType',
        ),
        migrations.AddField(
            model_name='m_partytype',
            name='IsDivision',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='m_partytype',
            name='IsSCM',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='m_parties',
            name='DivisionType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartiesDivision', to='FoodERPApp.M_PartyType'),
        ),
        migrations.DeleteModel(
            name='M_DivisionType',
        ),
        migrations.AddField(
            model_name='m_pricelist',
            name='DivisionType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartyTypeDivision', to='FoodERPApp.M_PartyType'),
        ),
        migrations.AlterField(
            model_name='m_parties',
            name='PartyType',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartyType', to='FoodERPApp.M_PriceList'),
        ),
    ]
