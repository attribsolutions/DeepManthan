# Generated by Django 3.0.8 on 2023-09-18 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0168_t_claimtrackingentry_party'),
    ]

    operations = [
        migrations.RenameField(
            model_name='t_claimtrackingentry',
            old_name='CreditoteAmount',
            new_name='CreditNoteAmount',
        ),
        migrations.RenameField(
            model_name='t_claimtrackingentry',
            old_name='year',
            new_name='Year',
        ),
        migrations.AlterField(
            model_name='t_claimtrackingentry',
            name='TypeOfClaim',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
