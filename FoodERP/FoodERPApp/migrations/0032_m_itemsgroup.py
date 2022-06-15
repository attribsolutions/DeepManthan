# Generated by Django 3.0.8 on 2022-06-15 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0031_delete_m_itemsgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_ItemsGroup',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=500)),
                ('Sequence', models.DecimalField(decimal_places=2, max_digits=5)),
                ('isActive', models.BooleanField(default=False)),
                ('CreatedBy', models.IntegerField(default=False)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField(default=False)),
                ('UpdatedOn', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'M_ItemsGroup',
            },
        ),
    ]
