# Generated by Django 3.0.8 on 2024-01-29 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0250_remove_t_purchasereturn_asmapprovalupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_purchasereturn',
            name='ASMApprovalImgUpload',
            field=models.FileField(blank=True, default='', null=True, upload_to='Images\\ReturnASMApprovalImgUpload'),
        ),
    ]
