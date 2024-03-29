# Generated by Django 3.0.8 on 2023-09-05 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0153_remove_t_creditdebitnotes_invoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_ChannelWiseItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ChannelItem', to='FoodERPApp.M_Items')),
                ('PartyType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ChannelPartyType', to='FoodERPApp.M_PartyType')),
            ],
            options={
                'db_table': 'M_ChannelWiseItems',
            },
        ),
    ]
