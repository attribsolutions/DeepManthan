# Generated by Django 3.0.8 on 2023-06-29 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0051_t_grns_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_grnitems',
            name='ActualQuantity',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=20),
            preserve_default=False,
        ),
    ]
