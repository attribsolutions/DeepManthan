# Generated by Django 3.0.8 on 2023-06-21 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0025_m_units_ewaybillunit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tc_invoiceuploads',
            old_name='EwayBillNo',
            new_name='AckNo',
        ),
        migrations.RenameField(
            model_name='tc_invoiceuploads',
            old_name='CancelBy',
            new_name='CanceledBy',
        ),
        migrations.RenameField(
            model_name='tc_invoiceuploads',
            old_name='InvoicePdf',
            new_name='EInvoicePdf',
        ),
        migrations.RenameField(
            model_name='tc_invoiceuploads',
            old_name='IRN_ACKNO',
            new_name='Irn',
        ),
    ]
