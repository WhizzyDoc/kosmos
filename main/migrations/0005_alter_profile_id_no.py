# Generated by Django 4.2.6 on 2023-10-21 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_profile_age_remove_profile_date_of_entry_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='id_no',
            field=models.CharField(max_length=15, unique=True, verbose_name='ID Number'),
        ),
    ]