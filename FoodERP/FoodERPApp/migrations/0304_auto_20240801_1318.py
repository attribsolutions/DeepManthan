# Generated by Django 3.0.8 on 2024-08-01 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0303_m_itemsupplier_supplierid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='m_itemsupplier',
            old_name='ItemID',
            new_name='Item',
        ),
        migrations.RenameField(
            model_name='m_itemsupplier',
            old_name='SupplierID',
            new_name='Supplier',
        ),
    ]
