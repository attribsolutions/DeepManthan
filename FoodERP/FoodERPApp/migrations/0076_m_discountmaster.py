# Generated by Django 3.0.8 on 2023-07-19 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0075_auto_20230719_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_DiscountMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FromDate', models.DateField()),
                ('ToDate', models.DateField()),
                ('DiscountType', models.IntegerField()),
                ('Discount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now_add=True)),
                ('PartyType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='DiscountPartyType', to='FoodERPApp.M_PartyType')),
            ],
            options={
                'db_table': 'M_DiscountMaster',
            },
        ),
    ]
