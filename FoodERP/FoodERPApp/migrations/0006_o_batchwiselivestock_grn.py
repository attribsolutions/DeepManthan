# Generated by Django 3.0.8 on 2022-12-30 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0005_auto_20221229_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='o_batchwiselivestock',
            name='GRN',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='GRN', to='FoodERPApp.T_GRNs'),
            preserve_default=False,
        ),
    ]
