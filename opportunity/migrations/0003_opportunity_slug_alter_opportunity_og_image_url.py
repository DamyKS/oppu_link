# Generated by Django 5.1.6 on 2025-03-07 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunity', '0002_opportunity_og_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='og_image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
