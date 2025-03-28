# Generated by Django 3.0.8 on 2025-03-10 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0345_m_roles_identifykey'),
    ]

    operations = [
        migrations.CreateModel(
            name='MC_SchemeItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TypeForItem', models.IntegerField()),
                ('Item', models.IntegerField()),
                ('SchemeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='SchemeIDForItems', to='FoodERPApp.M_Scheme')),
            ],
            options={
                'db_table': 'MC_SchemeItems',
            },
        ),
    ]
