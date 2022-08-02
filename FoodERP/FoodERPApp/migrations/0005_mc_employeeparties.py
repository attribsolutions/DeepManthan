# Generated by Django 3.0.8 on 2022-08-02 12:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0004_merge_20220802_1238'),
    ]

    operations = [
        migrations.CreateModel(
            name='MC_EmployeeParties',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('EmployeeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Employees', to='FoodERPApp.M_Employees')),
                ('Party', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Employeeparty', to='FoodERPApp.M_Parties')),
            ],
            options={
                'db_table': 'MC_EmployeeParties',
            },
        ),
    ]
