# Generated by Django 3.0.8 on 2022-08-24 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0035_auto_20220823_1828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abc',
            name='Name',
        ),
        migrations.RemoveField(
            model_name='abc',
            name='SurName',
        ),
        migrations.RemoveField(
            model_name='abc',
            name='otp',
        ),
        migrations.RemoveField(
            model_name='abc',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='abc',
            name='pincode',
        ),
        migrations.AddField(
            model_name='abc',
            name='Image',
            field=models.FileField(default=1, upload_to=''),
            preserve_default=False,
        ),
    ]
