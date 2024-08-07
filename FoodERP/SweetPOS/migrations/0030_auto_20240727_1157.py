# Generated by Django 3.0.8 on 2024-07-27 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0029_m_sposratemaster'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_sweetposuser',
            name='POSRateType',
            field=models.IntegerField(default=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='t_sposdeletedinvoices',
            name='Invoice',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='SPOSDeletedInvoiceUploads', to='SweetPOS.T_SPOSInvoices'),
            preserve_default=False,
        ),
    ]
