from django.db import models
from django.contrib.auth.models import User


# model for post
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,null=False)
    created_at = models.DateTimeField(auto_now_add=True) # automatically set when the post is created
    updated_at = models.DateTimeField(auto_now=True) # automatically updated every time the post is updated

    class Meta:
        db_table = 'post'

    def __str__(self):
        return self.title

# model for commnet
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments') # fetch comments on a post
    author = models.ForeignKey(User, on_delete=models.CASCADE,null=False) # fetch user comments
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment'

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'