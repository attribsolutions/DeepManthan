# Generated by Django 3.0.8 on 2023-11-03 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0214_t_claimtrackingentry_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='t_claimtrackingentry',
            name='File',
        ),
        migrations.AlterField(
            model_name='t_claimtrackingentry',
            name='CreditNoteUpload',
            field=models.FileField(blank=True, default='', null=True, upload_to='Images\\ClaimTrackingFiles'),
        ),
    ]