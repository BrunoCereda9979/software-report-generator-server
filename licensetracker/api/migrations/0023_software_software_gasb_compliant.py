# Generated by Django 5.0.9 on 2024-12-16 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_software_software_operational_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='software',
            name='software_gasb_compliant',
            field=models.BooleanField(default=False, help_text='Indicates if the software complies with Governmental Accounting Standards Board requirements', verbose_name='GASB Compliant'),
        ),
    ]