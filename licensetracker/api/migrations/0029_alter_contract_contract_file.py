# Generated by Django 5.0.9 on 2025-02-04 13:39

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_remove_software_software_contract_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='contract_file',
            field=models.FileField(upload_to=api.models.contract_upload_to),
        ),
    ]
