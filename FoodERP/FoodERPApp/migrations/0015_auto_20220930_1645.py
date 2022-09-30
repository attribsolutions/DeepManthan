# Generated by Django 3.0.8 on 2022-09-30 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0014_m_termsandconditions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='t_orders',
            name='Party',
        ),
        migrations.AddField(
            model_name='t_orders',
            name='Supplier',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='OrderSupplier', to='FoodERPApp.M_Parties'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='MC_PartySubParty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Party', to='FoodERPApp.M_Parties')),
                ('SubParty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='SubParty', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'MC_PartySubParty',
            },
        ),
    ]
