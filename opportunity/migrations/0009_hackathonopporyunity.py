# Generated by Django 5.1.6 on 2025-03-09 08:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunity', '0008_opportunity_og_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='HackathonOpporyunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail_link', models.URLField(max_length=500)),
                ('img', models.URLField(blank=True, max_length=500, null=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.CharField(blank=True, max_length=200, null=True)),
                ('time_left', models.CharField(max_length=50)),
                ('location', models.CharField(max_length=100)),
                ('prize', models.CharField(max_length=100)),
                ('participants', models.CharField(max_length=50)),
                ('host', models.CharField(max_length=100)),
                ('date_range', models.CharField(max_length=100)),
                ('themes', models.JSONField()),
                ('description', models.TextField()),
                ('date_posted', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-date_posted'],
            },
        ),
    ]
