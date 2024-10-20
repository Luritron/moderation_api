from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

class CommentSchema(BaseModel):
    id: int
    post_id: int
    content: str
    created_date: datetime

    class Config:
        from_attributes = True

class PostCommentSchema(BaseModel):
    id: int
    title: str
    content: str
    created_date: datetime
    comments: List[CommentSchema] = []

    @classmethod
    def from_orm(cls, obj):
        # Преобразуем комментарии
        comments = [CommentSchema.from_orm(comment) for comment in obj.comments.all()]
        return cls(id=obj.id, title=obj.title, content=obj.content, created_date=obj.created_date, comments=comments)

    class Config:
        from_attributes = True

class CreatePostSchema(BaseModel):
    title: str
    content: str

class CreateCommentSchema(BaseModel):
    post_id: int
    content: str