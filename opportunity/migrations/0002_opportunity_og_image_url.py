# Generated by Django 5.1.6 on 2025-03-06 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunity', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='og_image_url',
            field=models.URLField(blank=True),
        ),
    ]
