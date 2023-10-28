# Generated by Django 4.2.6 on 2023-10-28 09:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import tinymce.models


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
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='Site Title')),
                ('tagline', models.CharField(blank=True, max_length=100, null=True, verbose_name='Site Tagline')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='site/logo/')),
                ('about', tinymce.models.HTMLField(blank=True, null=True, verbose_name='About Organization')),
                ('objectives', tinymce.models.HTMLField(blank=True, null=True)),
                ('mission', tinymce.models.HTMLField(blank=True, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('post', tinymce.models.HTMLField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('active', models.BooleanField(default=True)),
                ('verified', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile')),
                ('category', models.ForeignKey(choices=[], on_delete=django.db.models.deletion.DO_NOTHING, related_name='news', to='admins.newscategory')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', tinymce.models.HTMLField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.CharField(choices=[('online', 'online'), ('live', 'live')], max_length=50)),
                ('location', models.CharField(blank=True, max_length=256, null=True)),
                ('link', models.URLField(blank=True, null=True)),
                ('directions', tinymce.models.HTMLField(blank=True, null=True)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
