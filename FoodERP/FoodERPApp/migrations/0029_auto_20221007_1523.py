# Generated by Django 3.0.8 on 2022-10-07 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0028_m_pages_iseditpopuporcomponent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mc_itemgsthsncode',
            name='Item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GSTHSNDetails', to='FoodERPApp.M_Items'),
        ),
        migrations.CreateModel(
            name='M_GSTHSNCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('EffectiveDate', models.DateField()),
                ('GSTPercentage', models.DecimalField(decimal_places=2, max_digits=10)),
                ('HSNCode', models.CharField(max_length=500)),
                ('CommonID', models.IntegerField(blank=True, null=True)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now_add=True)),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ItemGSTHSNDetails', to='FoodERPApp.M_Items')),
            ],
            options={
                'db_table': 'M_GSTHSNCode',
            },
        ),
    ]
