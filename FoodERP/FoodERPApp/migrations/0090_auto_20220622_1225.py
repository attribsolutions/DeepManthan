# Generated by Django 3.0.8 on 2022-06-22 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0089_m_designations_m_employeetype_m_state'),
    ]

    operations = [
        migrations.DeleteModel(
            name='M_Designations',
        ),
        migrations.DeleteModel(
            name='M_EmployeeType',
        ),
        migrations.DeleteModel(
            name='M_State',
        ),
    ]
