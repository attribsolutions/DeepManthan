# Generated by Django 3.0.8 on 2024-06-11 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0291_tc_challanreferences'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_challanreferences',
            name='Demands',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ChallanDemandReferences', to='FoodERPApp.T_Demands'),
        ),
    ]
