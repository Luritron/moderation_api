# tasks.py
from celery import shared_task
from .models import Comment, Post
import ollama
from django.utils import timezone

@shared_task
def generate_auto_reply(comment_id):
    comment = Comment.objects.get(id=comment_id)
    post = comment.post

    # Generating answer by Gemma 2
    response = ollama.generate(
        model="gemma2:2b",
        prompt=f"""
            Based on the following post:
            "{post.content}"
            and comment:
            "{comment.content}",
            generate a relevant response of up to 100 characters. Maximum.
            """
    )

    reply_content = response['response']
    Comment.objects.create(post=post, content=reply_content, created_date=timezone.now())
