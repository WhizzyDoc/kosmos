# Generated by Django 4.1.4 on 2023-11-09 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_query'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='log',
            options={'ordering': ['-date']},
        ),
        migrations.RemoveField(
            model_name='reward',
            name='owner',
        ),
        migrations.AddField(
            model_name='reward',
            name='title',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]