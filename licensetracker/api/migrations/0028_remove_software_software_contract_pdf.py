# Generated by Django 5.0.9 on 2025-01-07 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_contract'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='software',
            name='software_contract_pdf',
        ),
    ]
