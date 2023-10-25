# Generated by Django 4.2.6 on 2023-10-21 17:45

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rewards',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reward_type', models.CharField(max_length=100)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.profile')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('post', models.TextField()),
                ('date', models.DateTimeField(default=datetime.datetime(2023, 10, 21, 18, 44, 56, 267050))),
                ('featured', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile')),
                ('category', models.ForeignKey(choices=[], on_delete=django.db.models.deletion.DO_NOTHING, related_name='news', to='admins.newscategory')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('date', models.DateTimeField()),
                ('type', models.CharField(choices=[('online', 'online'), ('live', 'live')], max_length=50)),
                ('location', models.CharField(max_length=256)),
                ('directions', models.TextField()),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile')),
            ],
        ),
    ]