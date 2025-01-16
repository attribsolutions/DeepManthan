# Generated by Django 3.0.8 on 2025-01-13 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0328_auto_20250102_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_Scheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SchemeName', models.CharField(max_length=100)),
                ('SchemeValue', models.IntegerField()),
                ('ValueIn', models.CharField(max_length=100)),
                ('FromPeriod', models.DateField()),
                ('ToPeriod', models.DateField()),
                ('FreeItemID', models.IntegerField()),
                ('VoucherLimit', models.IntegerField()),
                ('QRPrefix', models.CharField(max_length=50)),
                ('IsActive', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'M_Scheme',
            },
        ),
        migrations.CreateModel(
            name='M_SchemeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SchemeTypeName', models.CharField(max_length=100)),
                ('Usage', models.CharField(max_length=50)),
                ('UsageType', models.CharField(max_length=50)),
                ('BillEffect', models.BooleanField(default=False)),
                ('IsQRApplicable', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'M_SchemeType',
            },
        ),
        
        migrations.CreateModel(
            name='MC_SchemeQRs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('QRCode', models.CharField(max_length=100)),
                ('SchemeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='SchemeIDforQR', to='FoodERPApp.M_Scheme')),
            ],
            options={
                'db_table': 'M_SchemeQRs',
            },
        ),
        migrations.AddField(
            model_name='m_scheme',
            name='SchemeTypeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='SchemeTypeID', to='FoodERPApp.M_SchemeType'),
        ),
    ]