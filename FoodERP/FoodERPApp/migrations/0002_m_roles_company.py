# Generated by Django 3.0.8 on 2023-03-08 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_roles',
            name='Company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='RoleCompany', to='FoodERPApp.C_Companies'),
            preserve_default=False,
        ),
    ]
