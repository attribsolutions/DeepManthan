# Generated by Django 3.0.8 on 2022-08-22 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0022_m_items_itemgroup'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MC_ItemsShelfLife',
            new_name='M_ItemsShelfLife',
        ),
        migrations.AlterModelTable(
            name='m_itemsshelflife',
            table='M_ItemsShelfLife',
        ),
    ]
