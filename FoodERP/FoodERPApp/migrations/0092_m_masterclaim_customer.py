# Generated by Django 3.0.8 on 2023-07-28 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0091_m_masterclaim_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_masterclaim',
            name='Customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ClaimCustomer', to='FoodERPApp.M_Parties'),
        ),
    ]
