# Generated by Django 5.0.9 on 2024-12-31 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_analytics_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='software',
            name='software_contract_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
