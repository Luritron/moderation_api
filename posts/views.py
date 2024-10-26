from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from ninja_jwt.authentication import JWTAuth
from .models import Post, Comment
from .schemas import PostCommentSchema, CommentSchema, CreatePostSchema, CreateCommentSchema, UserSchema, AnalyticsSchema
from typing import List
from datetime import datetime
from .tasks import generate_auto_reply

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Count
from django.db.models.functions import TruncDate

import ollama

api = NinjaAPI()

from ninja_jwt.tokens import RefreshToken


@api.post("/register")
def register(request, payload: UserSchema):
    if User.objects.filter(username=payload.username).exists():
        return api.create_response(request, {"error": "Пользователь уже существует"}, status=400)

    user = User.objects.create_user(username=payload.username, password=payload.password)
    return {"success": f"Пользователь {user.username} успешно зарегистрирован"}

# JWT token
@api.post("/login")
def login_user(request, payload: UserSchema):
    user = authenticate(username=payload.username, password=payload.password)
    if user is None:
        return api.create_response(request, {"error": "Неверные учетные данные"}, status=401)

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
    }

# Moderation by model Gemma 2
def moderate_content(content):
    response = ollama.generate(
        model="gemma2:2b",
        prompt=f"""
                Please check the following text for inappropriate content such as: foul language, insults and other inappropriate content. Answer only ‘Appropriate’ or ‘Not Approved’.
                Text: '{content}'
                """
    )
    return True if "Appropriate" in response['response'] else False

# List of posts
@api.get('/posts', response=List[PostCommentSchema], auth=JWTAuth())
def get_posts(request):
    posts = Post.objects.all()
    post_data = []
    for post in posts:
        comments = [CommentSchema.from_orm(comment) for comment in post.comments.all()]
        post_schema = PostCommentSchema.from_orm(post)
        post_schema.comments = comments
        post_data.append(post_schema)
    return post_data

@api.post('/posts', response=PostCommentSchema, auth=JWTAuth())
def create_post(request, payload: CreatePostSchema):
    if not moderate_content(payload.content):
        return api.create_response(request, {"error": "Post contains inappropriate text"}, status=400)

    post = Post.objects.create(**payload.dict())

    return PostCommentSchema.from_orm(post)

# List of comments by post_id
@api.get('/posts/{post_id}/comments', response=List[CommentSchema], auth=JWTAuth())
def get_comments(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)

    return [CommentSchema.from_orm(comment) for comment in post.comments.all()]

@api.post('/posts/{post_id}/comments', response=CommentSchema, auth=JWTAuth())
def create_comment(request, post_id: int, payload: CreateCommentSchema):
    if not moderate_content(payload.content):
        return api.create_response(request, {"error": "Comment contains inappropriate text"}, status=400)

    post = get_object_or_404(Post, pk=post_id)
    comment = Comment.objects.create(post=post, **payload.dict())

    # Check if automatic reply is enabled for the post
    if post.auto_reply_enabled:
        delay_time = post.auto_reply_delay_minutes
        # Running worker process
        generate_auto_reply.apply_async((comment.id,), countdown=delay_time)

    return CommentSchema.from_orm(comment)

# List of comments by timestamp
@api.get('/comments-daily-breakdown', response=List[AnalyticsSchema], auth=JWTAuth())
def comments_daily_breakdown(request, date_from: str, date_to: str):
    try:
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        return api.create_response(request, {"error": "Incorrect date format. Use YYYYY-MM-DD"}, status=400)

    comments = Comment.objects.filter(created_date__range=[date_from, date_to]) \
                              .annotate(day=TruncDate('created_date')) \
                              .values('day') \
                              .annotate(count=Count('id')) \
                              .order_by('day')

    return [{"date": item['day'], "count": item['count']} for item in comments]
