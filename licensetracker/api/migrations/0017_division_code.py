# Generated by Django 5.0.9 on 2024-10-21 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_alter_contactperson_contact_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='division',
            name='code',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
