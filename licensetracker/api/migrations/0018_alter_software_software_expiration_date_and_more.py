# Generated by Django 5.0.9 on 2024-10-21 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_division_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='software_expiration_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='software',
            name='software_last_updated',
            field=models.DateField(blank=True, null=True),
        ),
    ]
