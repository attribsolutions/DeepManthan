# Generated by Django 3.0.8 on 2023-06-05 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0033_auto_20230605_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_parties',
            name='City',
            field=models.ForeignKey(default=456, on_delete=django.db.models.deletion.DO_NOTHING, related_name='PartiesCities', to='FoodERPApp.M_Cities'),
            preserve_default=False,
        ),
    ]
