# Generated by Django 3.0.8 on 2023-07-19 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0077_m_discountmaster_pricelist'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_discountmaster',
            name='Customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='DiscountCustomer', to='FoodERPApp.M_Parties'),
        ),
    ]
