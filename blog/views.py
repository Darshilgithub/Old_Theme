from django.shortcuts import render, get_object_or_404
from .models import BlogPost  # ✅ Correct model name

def blog_home(request):
    posts = BlogPost.objects.all()
    return render(request, 'blog/blog_home.html', {'posts': posts})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'blog/blog_detail.html', {'post': post})
