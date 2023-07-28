# Generated by Django 3.0.8 on 2023-07-28 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0093_m_masterclaim_party'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_masterclaim',
            name='ItemReason',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='ClaimItemReason', to='FoodERPApp.M_GeneralMaster'),
            preserve_default=False,
        ),
    ]
