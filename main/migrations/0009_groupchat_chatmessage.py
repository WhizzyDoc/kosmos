# Generated by Django 4.1.4 on 2023-11-06 10:16

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_task_assigned_to_alter_task_completed_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_chat', to='main.department')),
                ('members', models.ManyToManyField(blank=True, related_name='department_group', to='main.profile')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='main.groupchat')),
                ('seen_by', models.ManyToManyField(related_name='chat_seen', to='main.profile')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sent', to='main.profile')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
    ]
