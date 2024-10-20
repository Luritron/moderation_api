from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from .models import Post, Comment
from .schemas import PostCommentSchema, CommentSchema, CreatePostSchema, CreateCommentSchema
from typing import List

import ollama

api = NinjaAPI()

def moderate_content(content):
    response = ollama.generate(
        model="gemma2:2b",
        prompt=f"""
                Пожалуйста, проверьте следующий текст на наличие такого неприемлемого содержания, как: нецензурная лексика, оскорбления и прочее. Ответьте только "Appropriate" или "Not Approved".
                Текст: '{content}'
                """
    )
    return True if "Appropriate" in response['response'] else False


@api.get('/posts', response=List[PostCommentSchema])
def get_posts(request):
    posts = Post.objects.all()
    post_data = []
    for post in posts:
        comments = [CommentSchema.from_orm(comment) for comment in post.comments.all()]  # Преобразуем комментарии
        post_schema = PostCommentSchema.from_orm(post)
        post_schema.comments = comments  # Устанавливаем комментарии
        post_data.append(post_schema)
    return post_data

@api.post('/posts', response=PostCommentSchema)
def create_post(request, payload: CreatePostSchema):
    if not moderate_content(payload.content):
        return api.create_response(request, {"error": "Пост содержит неприемлимый текст"}, status=400)

    # Создаем пост
    post = Post.objects.create(**payload.dict())

    # Возвращаем данные поста, включая преобразованные комментарии
    return PostCommentSchema.from_orm(post)

@api.get('/posts/{post_id}/comments', response=List[CommentSchema])
def get_comments(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    return [CommentSchema.from_orm(comment) for comment in post.comments.all()]

@api.post('/posts/{post_id}/comments', response=CommentSchema)
def create_comment(request, post_id: int, payload: CreateCommentSchema):
    if not moderate_content(payload.content):
        return api.create_response(request, {"error": "Комментарий содержит неприемлимый текст"}, status=400)

    post = get_object_or_404(Post, pk=post_id)
    comment = Comment.objects.create(post=post, **payload.dict())
    return CommentSchema.from_orm(comment)
