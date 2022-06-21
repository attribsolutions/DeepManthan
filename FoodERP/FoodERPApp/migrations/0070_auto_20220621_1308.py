# Generated by Django 3.0.8 on 2022-06-21 07:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0069_m_employees_working_hours'),
    ]

    operations = [
        migrations.CreateModel(
            name='T_Invoices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('InvoiceDate', models.DateField(auto_now_add=True)),
                ('CustomerID', models.IntegerField()),
                ('InvoiceNumber', models.IntegerField(blank=True, null=True)),
                ('FullInvoiceNumber', models.CharField(max_length=500)),
                ('CustomerGSTTin', models.CharField(max_length=500)),
                ('GrandTotal', models.DecimalField(decimal_places=2, max_digits=15)),
                ('PartyID', models.IntegerField(blank=True, null=True)),
                ('RoundOffAmount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('CreatedBy', models.IntegerField(blank=True, null=True)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField(blank=True, null=True)),
                ('UpdatedOn', models.DateTimeField(auto_now_add=True)),
                ('OrderID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FoodERPApp.T_Orders')),
            ],
            options={
                'db_table': 'T_Invoices',
            },
        ),
        migrations.AlterField(
            model_name='tc_invoiceitembatches',
            name='InvoiceID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FoodERPApp.T_Invoices'),
        ),
        migrations.AlterField(
            model_name='tc_invoiceitems',
            name='InvoiceID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InvoiceItems', to='FoodERPApp.T_Invoices'),
        ),
        migrations.DeleteModel(
            name='T_Invoice',
        ),
    ]
