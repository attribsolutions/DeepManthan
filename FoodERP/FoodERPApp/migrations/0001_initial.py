# Generated by Django 3.0.8 on 2022-07-16 15:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Abc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'Abc',
            },
        ),
        migrations.CreateModel(
            name='C_Companies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('Address', models.CharField(blank=True, max_length=100, null=True)),
                ('GSTIN', models.CharField(max_length=100)),
                ('PhoneNo', models.CharField(blank=True, max_length=100, null=True)),
                ('CompanyAbbreviation', models.CharField(max_length=100)),
                ('EmailID', models.CharField(blank=True, max_length=100, null=True)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'C_Companies',
            },
        ),
        migrations.CreateModel(
            name='C_CompanyGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'C_CompanyGroups',
            },
        ),
        migrations.CreateModel(
            name='H_Modules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('DisplayIndex', models.IntegerField()),
                ('isActive', models.BooleanField(default=False)),
                ('Icon', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField(blank=True, null=True)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField(blank=True, null=True)),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'H_Modules',
            },
        ),
        migrations.CreateModel(
            name='H_PageAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'H_PageAccess',
            },
        ),
        migrations.CreateModel(
            name='M_Designations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_Designations',
            },
        ),
        migrations.CreateModel(
            name='M_Districts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_Districts',
            },
        ),
        migrations.CreateModel(
            name='M_DivisionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_DivisionType',
            },
        ),
        migrations.CreateModel(
            name='M_Employees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('Address', models.CharField(max_length=500)),
                ('Mobile', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=255)),
                ('DOB', models.CharField(max_length=100)),
                ('PAN', models.CharField(max_length=100)),
                ('AadharNo', models.CharField(max_length=100)),
                ('working_hours', models.DecimalField(decimal_places=2, max_digits=15)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='EmployeesCompany', to='FoodERPApp.C_Companies')),
                ('Designation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='EmployeesDesignation', to='FoodERPApp.M_Designations')),
                ('District', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='EmployeesDistrict', to='FoodERPApp.M_Districts')),
            ],
            options={
                'db_table': 'M_Employees',
            },
        ),
        migrations.CreateModel(
            name='M_EmployeeTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_EmployeeTypes',
            },
        ),
        migrations.CreateModel(
            name='M_Items',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=500)),
                ('Sequence', models.DecimalField(decimal_places=2, max_digits=5)),
                ('GSTPercentage', models.DecimalField(decimal_places=2, max_digits=10)),
                ('MRP', models.DecimalField(decimal_places=2, max_digits=20)),
                ('Rate', models.DecimalField(decimal_places=2, max_digits=20)),
                ('isActive', models.BooleanField(default=False)),
                ('CreatedBy', models.IntegerField(default=False)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField(default=False)),
                ('UpdatedOn', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'M_Items',
            },
        ),
        migrations.CreateModel(
            name='M_ItemsGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=500)),
                ('Sequence', models.DecimalField(decimal_places=2, max_digits=5)),
                ('isActive', models.BooleanField(default=False)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_ItemsGroup',
            },
        ),
        migrations.CreateModel(
            name='M_Pages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('Description', models.CharField(blank=True, max_length=100)),
                ('isActive', models.BooleanField(default=False)),
                ('DisplayIndex', models.IntegerField()),
                ('Icon', models.CharField(max_length=100)),
                ('ActualPagePath', models.CharField(max_length=100)),
                ('isShowOnMenu', models.BooleanField(default=False)),
                ('PageType', models.IntegerField()),
                ('RelatedPageID', models.IntegerField()),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Module', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PagesModule', to='FoodERPApp.H_Modules')),
            ],
            options={
                'db_table': 'M_Pages',
            },
        ),
        migrations.CreateModel(
            name='M_Parties',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=500)),
                ('CustomerDivision', models.IntegerField()),
                ('Email', models.EmailField(max_length=200)),
                ('MobileNo', models.BigIntegerField()),
                ('AlternateContactNo', models.CharField(max_length=500)),
                ('Address', models.CharField(max_length=500)),
                ('PIN', models.CharField(max_length=500)),
                ('Taluka', models.IntegerField()),
                ('City', models.IntegerField()),
                ('GSTIN', models.CharField(max_length=500)),
                ('PAN', models.CharField(max_length=500)),
                ('FSSAINo', models.CharField(max_length=500)),
                ('FSSAIExipry', models.DateField(blank=True)),
                ('isActive', models.BooleanField(default=False)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartiesCompany', to='FoodERPApp.C_Companies')),
                ('District', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartiesDistrict', to='FoodERPApp.M_Districts')),
                ('DivisionType', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartiesDivision', to='FoodERPApp.M_DivisionType')),
            ],
            options={
                'db_table': 'M_Parties',
            },
        ),
        migrations.CreateModel(
            name='M_RoleAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='RoleAccessCompany', to='FoodERPApp.C_Companies')),
                ('Division', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='RoleAccessDividion', to='FoodERPApp.M_Parties')),
                ('Modules', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='RoleAccessModules', to='FoodERPApp.H_Modules')),
                ('Pages', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='RoleAccessPages', to='FoodERPApp.M_Pages')),
            ],
            options={
                'db_table': 'M_RoleAccess',
            },
        ),
        migrations.CreateModel(
            name='M_Roles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('Description', models.CharField(max_length=100)),
                ('isActive', models.BooleanField(default=False)),
                ('Dashboard', models.CharField(max_length=200)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_Roles',
            },
        ),
        migrations.CreateModel(
            name='M_States',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('StateCode', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_States',
            },
        ),
        migrations.CreateModel(
            name='M_Units',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=500)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'M_Units',
            },
        ),
        migrations.CreateModel(
            name='MC_ItemUnits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('BaseUnitQuantity', models.DecimalField(decimal_places=3, max_digits=5)),
                ('IsBase', models.IntegerField()),
                ('IsDefault', models.IntegerField()),
                ('IsSSUnit', models.IntegerField()),
                ('IsDeleted', models.BooleanField(default=False)),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ItemUnitsItemID', to='FoodERPApp.M_Items')),
                ('UnitID', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='UnitID', to='FoodERPApp.M_Units')),
            ],
            options={
                'db_table': 'MC_ItemUnits',
            },
        ),
        migrations.CreateModel(
            name='T_Invoices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('InvoiceDate', models.DateField()),
                ('InvoiceNumber', models.IntegerField()),
                ('FullInvoiceNumber', models.CharField(max_length=500)),
                ('CustomerGSTTin', models.CharField(max_length=500)),
                ('GrandTotal', models.DecimalField(decimal_places=2, max_digits=15)),
                ('RoundOffAmount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='InvoicesCustomer', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'T_Invoices',
            },
        ),
        migrations.CreateModel(
            name='T_Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('OrderDate', models.DateField()),
                ('OrderAmount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('Description', models.CharField(max_length=500)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now_add=True)),
                ('Customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='OrderCustomer', to='FoodERPApp.M_Items')),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='OrderParty', to='FoodERPApp.M_Items')),
            ],
            options={
                'db_table': 'T_Orders',
            },
        ),
        migrations.CreateModel(
            name='M_Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('LoginName', models.CharField(max_length=100, unique=True)),
                ('isActive', models.BooleanField(default=False)),
                ('isSendOTP', models.BooleanField(default=False)),
                ('isLoginUsingMobile', models.BooleanField(default=False)),
                ('isLoginUsingEmail', models.BooleanField(default=False)),
                ('AdminPassword', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('Employee', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='UserEmployee', to='FoodERPApp.M_Employees')),
            ],
            options={
                'db_table': 'M_Users',
            },
        ),
        migrations.CreateModel(
            name='TC_OrderItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('MRP', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('BaseUnitQuantity', models.DecimalField(decimal_places=2, max_digits=5)),
                ('GST', models.DecimalField(decimal_places=2, max_digits=5)),
                ('BasicAmount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('GSTAmount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('CGST', models.DecimalField(decimal_places=2, max_digits=20)),
                ('SGST', models.DecimalField(decimal_places=2, max_digits=20)),
                ('IGST', models.DecimalField(decimal_places=2, max_digits=20)),
                ('CGSTPercentage', models.DecimalField(decimal_places=2, max_digits=20)),
                ('SGSTPercentage', models.DecimalField(decimal_places=2, max_digits=20)),
                ('IGSTPercentage', models.DecimalField(decimal_places=2, max_digits=20)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Items', to='FoodERPApp.M_Items')),
                ('Order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderItem', to='FoodERPApp.T_Orders')),
                ('Unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='OrderUnitID', to='FoodERPApp.MC_ItemUnits')),
            ],
            options={
                'db_table': 'TC_OrderItems',
            },
        ),
        migrations.CreateModel(
            name='TC_InvoiceItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('HSNCode', models.CharField(max_length=500)),
                ('Quantity', models.DecimalField(decimal_places=3, max_digits=5)),
                ('BaseUnitQuantity', models.DecimalField(decimal_places=3, max_digits=15)),
                ('QtyInKg', models.DecimalField(decimal_places=3, max_digits=10)),
                ('QtyInNo', models.DecimalField(decimal_places=3, max_digits=10)),
                ('QtyInBox', models.DecimalField(decimal_places=3, max_digits=10)),
                ('MRP', models.DecimalField(decimal_places=2, max_digits=15)),
                ('Rate', models.DecimalField(decimal_places=2, max_digits=15)),
                ('BasicAmount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('TaxType', models.CharField(max_length=500)),
                ('GSTPercentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('GSTAmount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('Amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('DiscountType', models.CharField(max_length=500)),
                ('Discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('DiscountAmount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('CGST', models.DecimalField(decimal_places=2, max_digits=5)),
                ('SGST', models.DecimalField(decimal_places=2, max_digits=5)),
                ('IGST', models.DecimalField(decimal_places=2, max_digits=5)),
                ('CGSTPercentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('SGSTPercentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('IGSTPercentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('Invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InvoiceItems', to='FoodERPApp.T_Invoices')),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.M_Items')),
                ('Unit', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='InvoiceUnitID', to='FoodERPApp.MC_ItemUnits')),
            ],
            options={
                'db_table': 'TC_InvoiceItems',
            },
        ),
        migrations.CreateModel(
            name='TC_InvoiceItemBatches',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('BatchDate', models.DateField(blank=True, null=True)),
                ('BatchCode', models.CharField(max_length=500)),
                ('Quantity', models.DecimalField(decimal_places=3, max_digits=5)),
                ('MRP', models.DecimalField(decimal_places=2, max_digits=15)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('Invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FoodERPApp.T_Invoices')),
                ('InvoiceItem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='InvoiceItemBatches', to='FoodERPApp.TC_InvoiceItems')),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.M_Items')),
                ('Unit', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='InvoiceBatchUnitID', to='FoodERPApp.MC_ItemUnits')),
            ],
            options={
                'db_table': 'TC_InvoiceItemBatches',
            },
        ),
        migrations.AddField(
            model_name='t_invoices',
            name='Order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.T_Orders'),
        ),
        migrations.AddField(
            model_name='t_invoices',
            name='Party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='InvoicesParty', to='FoodERPApp.M_Parties'),
        ),
        migrations.CreateModel(
            name='MC_UserRoles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Role', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Role', to='FoodERPApp.M_Roles')),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserRole', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'MC_UserRoles',
            },
        ),
        migrations.CreateModel(
            name='MC_RolePageAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PageAccess', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='RolePageAccess', to='FoodERPApp.H_PageAccess')),
                ('RoleAccess', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='RoleAccess', to='FoodERPApp.M_RoleAccess')),
            ],
            options={
                'db_table': 'MC_RolePageAccess',
            },
        ),
        migrations.CreateModel(
            name='MC_PagePageAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Access', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='FoodERPApp.H_PageAccess')),
                ('Page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PagePageAccess', to='FoodERPApp.M_Pages')),
            ],
            options={
                'db_table': 'MC_PagePageAccess',
            },
        ),
        migrations.AddField(
            model_name='m_roleaccess',
            name='Role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='RoleAccessRole', to='FoodERPApp.M_Roles'),
        ),
        migrations.CreateModel(
            name='M_PartyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField()),
                ('UpdatedOn', models.DateTimeField(auto_now=True)),
                ('DivisionType', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartyTypeDivision', to='FoodERPApp.M_DivisionType')),
            ],
            options={
                'db_table': 'M_PartyType',
            },
        ),
        migrations.AddField(
            model_name='m_parties',
            name='PartyType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartiesPartyType', to='FoodERPApp.M_PartyType'),
        ),
        migrations.AddField(
            model_name='m_parties',
            name='State',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartiesState', to='FoodERPApp.M_States'),
        ),
        migrations.AddField(
            model_name='m_items',
            name='BaseUnitID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='BaseUnitID', to='FoodERPApp.M_Units'),
        ),
        migrations.AddField(
            model_name='m_items',
            name='ItemGroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ItemGroup', to='FoodERPApp.M_ItemsGroup'),
        ),
        migrations.AddField(
            model_name='m_employees',
            name='EmployeeType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='EmployeeType', to='FoodERPApp.M_EmployeeTypes'),
        ),
        migrations.AddField(
            model_name='m_employees',
            name='Party',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='EmployeesParty', to='FoodERPApp.M_Parties'),
        ),
        migrations.AddField(
            model_name='m_employees',
            name='State',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='EmployeesState', to='FoodERPApp.M_States'),
        ),
        migrations.AddField(
            model_name='m_districts',
            name='State',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='DistrictState', to='FoodERPApp.M_States'),
        ),
        migrations.AddField(
            model_name='c_companies',
            name='CompanyGroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='CompanyGroup', to='FoodERPApp.C_CompanyGroups'),
        ),
    ]
