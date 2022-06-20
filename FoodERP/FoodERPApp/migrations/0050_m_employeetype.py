# Generated by Django 3.0.8 on 2022-06-18 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0049_m_resion'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_EmployeeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('CreatedBy', models.IntegerField(blank=True, null=True)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'M_EmployeeType',
            },
        ),
    ]
