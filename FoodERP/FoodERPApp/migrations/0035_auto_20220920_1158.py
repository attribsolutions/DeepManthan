# Generated by Django 3.0.8 on 2022-09-20 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0034_m_marginmaster_m_mrpmaster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_pricelist',
            name='Company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='PriceListCompany', to='FoodERPApp.C_Companies'),
            preserve_default=False,
        ),
    ]
