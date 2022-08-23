# Generated by Django 3.0.8 on 2022-08-23 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0033_auto_20220823_1806'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mc_itemcategorydetails',
            name='ProductCategory',
        ),
        migrations.AddField(
            model_name='mc_itemcategorydetails',
            name='Category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Category', to='FoodERPApp.M_ProductCategory'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mc_itemcategorydetails',
            name='CategoryType',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='CategoryType', to='FoodERPApp.M_ProductCategoryType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mc_itemcategorydetails',
            name='SubCategory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='SubCategory', to='FoodERPApp.M_ProductSubCategory'),
            preserve_default=False,
        ),
    ]
