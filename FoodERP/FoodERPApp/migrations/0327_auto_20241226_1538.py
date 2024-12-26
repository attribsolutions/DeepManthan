# Generated by Django 3.0.8 on 2024-12-26 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0326_m_giftvouchercode'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_orderitems',
            name='OrderItem',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='m_giftvouchercode',
            name='VoucherType',
            field=models.ForeignKey(db_column='VoucherType_id', on_delete=django.db.models.deletion.PROTECT, related_name='GiftVoucherType', to='FoodERPApp.M_GeneralMaster'),
        ),
    ]
