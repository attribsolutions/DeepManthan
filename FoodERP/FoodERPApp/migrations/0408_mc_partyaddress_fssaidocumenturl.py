# Generated by Django 3.0.8 on 2025-06-20 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0407_auto_20250617_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='mc_partyaddress',
            name='fssaidocumenturl',
            field=models.FileField(blank=True, default='', null=True, upload_to='Images\\FSSAIDocuments'),
        ),
    ]
