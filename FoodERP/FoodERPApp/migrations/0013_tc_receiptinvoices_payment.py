# Generated by Django 3.0.8 on 2023-04-14 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0012_m_bank_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_receiptinvoices',
            name='Payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Payment', to='FoodERPApp.T_Receipts'),
        ),
    ]
