# Generated by Django 5.0 on 2024-06-22 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Event', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(default='', upload_to=''),
        ),
    ]
