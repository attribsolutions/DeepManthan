# Generated by Django 3.0.8 on 2025-04-14 18:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0373_m_accountgrouptype_m_ledger_t_voucher_tc_voucherdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_voucher',
            name='Invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vouvhers', to='FoodERPApp.T_Invoices'),
        ),
    ]
