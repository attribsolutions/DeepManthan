# Generated by Django 3.0.8 on 2024-07-20 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0028_auto_20240715_1710'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_SPOSRateMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('POSRateType', models.IntegerField()),
                ('IsChangeRateToDefault', models.BooleanField(default=False)),
                ('EffectiveFrom', models.DateField()),
                ('Rate', models.DecimalField(decimal_places=2, max_digits=15)),
                ('ItemID', models.IntegerField()),
            ],
            options={
                'db_table': 'M_SPOSRateMaster',
            },
        ),
    ]