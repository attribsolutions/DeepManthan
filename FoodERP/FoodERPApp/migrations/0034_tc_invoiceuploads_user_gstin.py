# Generated by Django 3.0.8 on 2023-06-22 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0033_auto_20230622_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_invoiceuploads',
            name='user_gstin',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
    ]
