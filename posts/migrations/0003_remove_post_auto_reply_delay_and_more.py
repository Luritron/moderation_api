# Generated by Django 5.1.2 on 2024-10-24 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_post_auto_reply_delay_post_auto_reply_enabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='auto_reply_delay',
        ),
        migrations.AddField(
            model_name='post',
            name='auto_reply_delay_minutes',
            field=models.IntegerField(default=10),
        ),
    ]
