# Generated by Django 3.0.8 on 2025-04-14 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0375_auto_20250414_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_voucher',
            name='CreditNote',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Voucher_CreditNote', to='FoodERPApp.T_CreditDebitNotes'),
        ),
    ]
