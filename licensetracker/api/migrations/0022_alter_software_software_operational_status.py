# Generated by Django 5.0.9 on 2024-11-13 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_software_software_annual_amount_detail_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='software_operational_status',
            field=models.CharField(choices=[('A', 'Active'), ('I', 'Inactive'), ('AU', 'Authorized')], default='A', max_length=2),
        ),
    ]
