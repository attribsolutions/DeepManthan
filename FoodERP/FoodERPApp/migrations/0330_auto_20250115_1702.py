# Generated by Django 3.0.8 on 2025-01-15 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0329_auto_20250113_1757'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MC_SchemeQRs',
            new_name='M_SchemeQRs',
        ),
        migrations.RenameField(
            model_name='m_schemetype',
            old_name='Usage',
            new_name='UsageTime',
        ),
        migrations.AddField(
            model_name='m_scheme',
            name='BillAbove',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='m_scheme',
            name='FreeItemID',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='m_scheme',
            name='FromPeriod',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='m_scheme',
            name='ToPeriod',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='m_scheme',
            name='VoucherLimit',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterModelTable(
            name='m_schemeqrs',
            table='MC_SchemeQRs',
        ),
        migrations.CreateModel(
            name='MC_SchemeParties',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PartyID', models.IntegerField()),
                ('SchemeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='SchemeIDForParties', to='FoodERPApp.M_Scheme')),
            ],
            options={
                'db_table': 'MC_SchemeParties',
            },
        ),
    ]