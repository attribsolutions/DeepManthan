# Generated by Django 3.0.8 on 2024-11-18 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0321_auto_20241113_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_mrpmaster',
            name='PartyType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='MRPMasterPartyType', to='FoodERPApp.M_PartyType'),
        ),
    ]
