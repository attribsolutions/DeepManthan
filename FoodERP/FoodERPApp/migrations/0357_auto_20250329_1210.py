# Generated by Django 3.0.8 on 2025-03-29 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0356_auto_20250329_1048'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='m_parties',
            index=models.Index(fields=['Company', 'SAPPartyCode'], name='M_Parties_Company_30c8fd_idx'),
        ),
        migrations.AddConstraint(
            model_name='m_parties',
            constraint=models.UniqueConstraint(fields=('Company', 'SAPPartyCode'), name='unique_company_SAPPartyCode'),
        ),
    ]
