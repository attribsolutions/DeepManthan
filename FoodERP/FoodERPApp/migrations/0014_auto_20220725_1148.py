# Generated by Django 3.0.8 on 2022-07-25 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0013_m_parties_isscm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_parties',
            name='IsSCM',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='IsSCM', to='FoodERPApp.C_Companies'),
        ),
    ]
