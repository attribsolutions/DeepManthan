# Generated by Django 3.0.8 on 2022-07-28 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0015_auto_20220728_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='mc_userroles',
            name='Party',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='userparty', to='FoodERPApp.M_Parties'),
            preserve_default=False,
        ),
    ]
