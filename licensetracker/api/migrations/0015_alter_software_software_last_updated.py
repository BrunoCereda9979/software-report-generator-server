# Generated by Django 5.0.9 on 2024-10-17 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_department_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='software_last_updated',
            field=models.DateField(null=True),
        ),
    ]
