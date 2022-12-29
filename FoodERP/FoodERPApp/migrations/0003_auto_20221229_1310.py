# Generated by Django 3.0.8 on 2022-12-29 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0002_auto_20221229_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mc_billofmaterialitems',
            name='Quantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='t_deliverychallans',
            name='GrandTotal',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='t_materialissue',
            name='LotQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='t_workorder',
            name='Quantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='tc_deliverychallanitems',
            name='Quantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='tc_materialissueitems',
            name='IssueQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='tc_materialissueitems',
            name='WorkOrderQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='tc_workorderitems',
            name='BomQuantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
        migrations.AlterField(
            model_name='tc_workorderitems',
            name='Quantity',
            field=models.DecimalField(decimal_places=3, max_digits=15),
        ),
    ]
