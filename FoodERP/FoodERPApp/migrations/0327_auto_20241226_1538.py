# Generated by Django 3.0.8 on 2024-12-26 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0325_m_users_isloginpermissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_orderitems',
            name='OrderItem',
            field=models.BooleanField(default=False),
        ),
        
    ]
