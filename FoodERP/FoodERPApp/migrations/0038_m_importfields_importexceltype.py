# Generated by Django 3.0.8 on 2023-06-06 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0037_m_importexceltypes'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_importfields',
            name='ImportExceltype',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ImportFieldExcelTypes', to='FoodERPApp.M_ImportExcelTypes'),
            preserve_default=False,
        ),
    ]
