# Generated by Django 5.0 on 2024-06-24 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Event', '0003_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='booking_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]