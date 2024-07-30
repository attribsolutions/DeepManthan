# Generated by Django 3.0.8 on 2024-04-11 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0273_auto_20240403_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_RateMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('EffectiveDate', models.DateField()),
                ('Rate', models.DecimalField(decimal_places=2, max_digits=20)),
                ('CommonID', models.IntegerField(blank=True, null=True)),
                ('IsDeleted', models.BooleanField(default=False)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='RateCompany', to='FoodERPApp.C_Companies')),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ItemRateDetails', to='FoodERPApp.M_Items')),
            ],
            options={
                'db_table': 'M_RateMaster',
            },
        ),
    ]
