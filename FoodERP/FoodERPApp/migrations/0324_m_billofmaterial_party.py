# Generated by Django 3.0.8 on 2024-11-22 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0323_m_gsthsncode_partytype'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_billofmaterial',
            name='Party',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='FoodERPApp.M_Parties'),
            preserve_default=False,
        ),
    ]
