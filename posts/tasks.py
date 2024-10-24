# tasks.py
from celery import shared_task
from .models import Comment, Post
import ollama
from django.utils import timezone
import time

@shared_task
def generate_auto_reply(comment_id):
    # Получаем комментарий
    comment = Comment.objects.get(id=comment_id)
    post = comment.post

    # Генерация релевантного ответа с помощью AI
    response = ollama.generate(
        model="gemma2:2b",
        prompt=f"""
            На основе следующего поста:
            "{post.content}"
            и комментария:
            "{comment.content}",
            сгенерируй релевантный ответ до 100 символов. Не более.
            """
    )

    # Добавляем новый комментарий-ответ
    reply_content = response['response']
    Comment.objects.create(post=post, content=reply_content, created_date=timezone.now())
