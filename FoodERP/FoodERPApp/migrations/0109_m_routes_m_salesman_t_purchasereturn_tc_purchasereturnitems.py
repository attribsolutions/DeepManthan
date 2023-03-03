# Generated by Django 3.0.8 on 2023-03-03 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0108_remove_t_orders_isopenpo'),
    ]

    operations = [
        migrations.CreateModel(
            name='T_PurchaseReturn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ReturnDate', models.DateField()),
                ('ReturnNumber', models.IntegerField()),
                ('FullReturnNumber', models.CharField(max_length=500)),
                ('GrandTotal', models.DecimalField(decimal_places=2, max_digits=15)),
                ('RoundOffAmount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ReturnCustomer', to='FoodERPApp.M_Parties')),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ReturnParty', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'T_PurchaseReturn',
            },
        ),
        migrations.CreateModel(
            name='TC_PurchaseReturnItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Quantity', models.DecimalField(decimal_places=3, max_digits=15)),
                ('BaseUnitQuantity', models.DecimalField(decimal_places=3, max_digits=15)),
                ('Rate', models.DecimalField(decimal_places=2, max_digits=15)),
                ('BasicAmount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('TaxType', models.CharField(max_length=500)),
                ('GSTAmount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('Amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('DiscountType', models.CharField(blank=True, max_length=500, null=True)),
                ('Discount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('DiscountAmount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('CGST', models.DecimalField(decimal_places=2, max_digits=15)),
                ('SGST', models.DecimalField(decimal_places=2, max_digits=15)),
                ('IGST', models.DecimalField(decimal_places=2, max_digits=15)),
                ('CGSTPercentage', models.DecimalField(decimal_places=2, max_digits=15)),
                ('SGSTPercentage', models.DecimalField(decimal_places=2, max_digits=15)),
                ('IGSTPercentage', models.DecimalField(decimal_places=2, max_digits=15)),
                ('BatchDate', models.DateField(blank=True, null=True)),
                ('BatchCode', models.CharField(max_length=500)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('GST', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ReturnItemGST', to='FoodERPApp.M_GSTHSNCode')),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='FoodERPApp.M_Items')),
                ('LiveBatch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='FoodERPApp.O_LiveBatches')),
                ('MRP', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ReturnItemMRP', to='FoodERPApp.M_MRPMaster')),
                ('PurchaseReturn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Returnitems', to='FoodERPApp.T_PurchaseReturn')),
                ('Unit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ReturnUnitID', to='FoodERPApp.MC_ItemUnits')),
            ],
            options={
                'db_table': 'TC_PurchaseReturnItems',
            },
        ),
        migrations.CreateModel(
            name='M_Salesman',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=500)),
                ('MobileNo', models.BigIntegerField()),
                ('IsActive', models.BooleanField(default=False)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='SCompany', to='FoodERPApp.C_Companies')),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='SParty', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'M_Salesman',
            },
        ),
        migrations.CreateModel(
            name='M_Routes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=500)),
                ('Sunday', models.BooleanField(blank=True, default=False, null=True)),
                ('Monday', models.BooleanField(blank=True, default=False, null=True)),
                ('Tuesday', models.BooleanField(blank=True, default=False, null=True)),
                ('Wednesday', models.BooleanField(blank=True, default=False, null=True)),
                ('Thursday', models.BooleanField(blank=True, default=False, null=True)),
                ('Friday', models.BooleanField(blank=True, default=False, null=True)),
                ('Saturday', models.BooleanField(blank=True, default=False, null=True)),
                ('IsActive', models.BooleanField(default=False)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='RCompany', to='FoodERPApp.C_Companies')),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='RParty', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'M_Routes',
            },
        ),
    ]
