# Generated by Django 3.0.8 on 2023-01-17 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0047_tc_demandsreferences'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_demandsreferences',
            name='MaterialIssue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='FoodERPApp.T_MaterialIssue'),
        ),
    ]
