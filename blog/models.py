from django.db import models
from django.utils import timezone

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    author = models.CharField(max_length=100, default='Admin')  # optional

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
