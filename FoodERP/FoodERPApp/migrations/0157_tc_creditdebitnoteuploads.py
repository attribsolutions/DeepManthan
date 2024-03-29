# Generated by Django 3.0.8 on 2023-09-06 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0156_m_channelwiseitems_partytype'),
    ]

    operations = [
        migrations.CreateModel(
            name='TC_CreditDebitNoteUploads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AckNo', models.CharField(max_length=500, null=True)),
                ('Irn', models.CharField(max_length=500, null=True)),
                ('QRCodeUrl', models.CharField(max_length=500, null=True)),
                ('EInvoicePdf', models.CharField(max_length=500, null=True)),
                ('EwayBillNo', models.CharField(max_length=500, null=True)),
                ('EwayBillUrl', models.CharField(max_length=500, null=True)),
                ('EInvoiceCreatedBy', models.IntegerField(null=True)),
                ('EInvoiceCreatedOn', models.DateTimeField(null=True)),
                ('EwayBillCreatedBy', models.IntegerField(null=True)),
                ('EwayBillCreatedOn', models.DateTimeField(null=True)),
                ('EInvoiceCanceledBy', models.IntegerField(null=True)),
                ('EInvoiceCanceledOn', models.DateTimeField(null=True)),
                ('EwayBillCanceledBy', models.IntegerField(null=True)),
                ('EwayBillCanceledOn', models.DateTimeField(null=True)),
                ('EInvoiceIsCancel', models.BooleanField(default=False)),
                ('EwayBillIsCancel', models.BooleanField(default=False)),
                ('user_gstin', models.CharField(max_length=500)),
                ('CRDRNote', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='CRDRNoteUploads', to='FoodERPApp.T_CreditDebitNotes')),
            ],
        ),
    ]
