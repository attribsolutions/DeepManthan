# Generated by Django 3.0.8 on 2024-12-04 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SweetPOS', '0054_m_sweetposmachine_servicetimeinterval'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_ServiceSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Party', models.IntegerField()),
                ('ServiceSettingsID', models.IntegerField()),
                ('Flag', models.BooleanField(default=False)),
                ('Value', models.CharField(blank=True, max_length=50, null=True)),
                ('Access', models.BooleanField(default=False)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedON', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'M_ServiceSettings',
            },
        ),
    ]