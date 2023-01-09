# Generated by Django 3.0.8 on 2023-01-09 12:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0027_auto_20230107_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_production',
            name='Unit',
            field=models.ForeignKey(default=301, on_delete=django.db.models.deletion.PROTECT, related_name='ProductionUnitID', to='FoodERPApp.MC_ItemUnits'),
            preserve_default=False,
        ),
    ]
