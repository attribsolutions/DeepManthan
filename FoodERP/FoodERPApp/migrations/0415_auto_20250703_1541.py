# Generated by Django 3.0.8 on 2025-07-03 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0414_auto_20250702_1308'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='mc_schemeparties',
            constraint=models.UniqueConstraint(fields=('SchemeID', 'PartyID'), name='unique_scheme_party'),
        ),
    ]
