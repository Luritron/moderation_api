from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from .models import Post, Comment
from .schemas import PostCommentSchema, CommentSchema, CreatePostSchema, CreateCommentSchema, UserSchema, AnalyticsSchema
from typing import List
from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.db.models.functions import TruncDate
from ninja.security import django_auth

import ollama

api = NinjaAPI()

# Регистрация
@api.post("/register")
def register(request, payload: UserSchema):
    if User.objects.filter(username=payload.username).exists():
        return api.create_response(request, {"error": "Пользователь уже существует"}, status=400)

    user = User.objects.create_user(username=payload.username, password=payload.password)
    return {"success": f"Пользователь {user.username} успешно зарегистрирован"}

# Вход
@api.post("/login")
def login_user(request, payload: UserSchema):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is None:
        return api.create_response(request, {"error": "Неверные учетные данные"}, status=401)

    login(request, user)
    return {"success": "Вы успешно вошли в систему"}

# Выход
@api.post("/logout")
def logout_user(request):
    logout(request)
    return {"success": "Вы вышли из системы"}


def moderate_content(content):
    response = ollama.generate(
        model="gemma2:2b",
        prompt=f"""
                Пожалуйста, проверьте следующий текст на наличие такого неприемлемого содержания, как: нецензурная лексика, оскорбления и прочее. Ответьте только "Appropriate" или "Not Approved".
                Текст: '{content}'
                """
    )
    return True if "Appropriate" in response['response'] else False


@api.get('/posts', response=List[PostCommentSchema], auth=django_auth)
def get_posts(request):
    posts = Post.objects.all()
    post_data = []
    for post in posts:
        comments = [CommentSchema.from_orm(comment) for comment in post.comments.all()]  # Преобразуем комментарии
        post_schema = PostCommentSchema.from_orm(post)
        post_schema.comments = comments  # Устанавливаем комментарии
        post_data.append(post_schema)
    return post_data

@api.post('/posts', response=PostCommentSchema, auth=django_auth)
def create_post(request, payload: CreatePostSchema):
    if not moderate_content(payload.content):
        return api.create_response(request, {"error": "Пост содержит неприемлимый текст"}, status=400)

    # Создаем пост
    post = Post.objects.create(**payload.dict())

    # Возвращаем данные поста, включая преобразованные комментарии
    return PostCommentSchema.from_orm(post)

@api.get('/posts/{post_id}/comments', response=List[CommentSchema], auth=django_auth)
def get_comments(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    return [CommentSchema.from_orm(comment) for comment in post.comments.all()]

@api.post('/posts/{post_id}/comments', response=CommentSchema, auth=django_auth)
def create_comment(request, post_id: int, payload: CreateCommentSchema):
    if not moderate_content(payload.content):
        return api.create_response(request, {"error": "Комментарий содержит неприемлимый текст"}, status=400)

    post = get_object_or_404(Post, pk=post_id)
    comment = Comment.objects.create(post=post, **payload.dict())
    return CommentSchema.from_orm(comment)

@api.get('/comments-daily-breakdown', response=List[AnalyticsSchema], auth=django_auth)
def comments_daily_breakdown(request, date_from: str, date_to: str):
    try:
        # Преобразуем строки в объекты datetime
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        return api.create_response(request, {"error": "Неверный формат дат. Используйте YYYY-MM-DD."}, status=400)

    # Фильтруем комментарии по указанному диапазону и группируем по дням
    comments = Comment.objects.filter(created_date__range=[date_from, date_to]) \
                              .annotate(day=TruncDate('created_date')) \
                              .values('day') \
                              .annotate(count=Count('id')) \
                              .order_by('day')

    # Возвращаем результат
    return [{"date": item['day'], "count": item['count']} for item in comments]