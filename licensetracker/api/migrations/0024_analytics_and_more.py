# Generated by Django 5.0.9 on 2024-12-30 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_software_software_gasb_compliant'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_spending', models.FloatField()),
            ],
        ),
        migrations.RenameField(
            model_name='software',
            old_name='software_annual_amount_detail',
            new_name='software_cost_detail',
        ),
        migrations.RenameField(
            model_name='software',
            old_name='software_annual_amount',
            new_name='software_monthly_cost',
        ),
    ]