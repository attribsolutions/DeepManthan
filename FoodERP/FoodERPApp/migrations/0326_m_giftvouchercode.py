# Generated by Django 3.0.8 on 2024-12-20 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0325_m_users_isloginpermissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_GiftVoucherCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('VoucherCode', models.CharField(max_length=50)),
                ('IsActive', models.BooleanField(default=False)),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('VoucherType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='GiftVoucherType', to='FoodERPApp.M_GeneralMaster')),
            ],
            options={
                'db_table': 'M_GiftVoucherCode',
            },
        ),
    ]