from django.db import models

# Create your models here.
class Post(models.Model):       # Post model
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    auto_reply_enabled = models.BooleanField(default=False)
    auto_reply_delay_minutes = models.IntegerField(default=10)

class Comment(models.Model):    # Comments model
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
