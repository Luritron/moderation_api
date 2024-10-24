# Generated by Django 5.1.2 on 2024-10-24 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_remove_post_auto_reply_delay_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='auto_reply_delay_minutes',
        ),
        migrations.AddField(
            model_name='post',
            name='reply_delay',
            field=models.IntegerField(default=60),
        ),
    ]
