# models.py
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from datetime import timedelta
from account.models import *
from functools import partial
import os
import re
from django.conf import settings

from django.contrib.auth.models import AbstractUser
def validate_file_extension(file, allowed_extensions):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file extension. Allowed extensions are: {', '.join(allowed_extensions)}"
        )

# Bind the allowed extensions for course_category images.
validate_category_image = partial(validate_file_extension, allowed_extensions=['.jpg', '.jpeg', '.png', '.gif', '.bmp'])
# Bind validator for other images
validate_image = partial(validate_file_extension, allowed_extensions=['.jpg', '.jpeg', '.png', '.gif', '.bmp'])

class course_category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # New image field for course_category
    image = models.ImageField(
        upload_to='course_category',  # Files saved under MEDIA_ROOT/course_category/
        blank=True,
        null=True,
        validators=[validate_category_image]
    )
    
    def __str__(self) -> str:
        return self.name
    
validate_video = partial(validate_file_extension, allowed_extensions=['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'])

class Courses(models.Model):
    level = (
        ('Beginner', 'Beginner'),
        ('Normal', 'Normal'),
        ('Pro', 'Pro')
    )
    thumbline_image = models.ImageField(upload_to='media/course_imgs', validators=[validate_image])
    intro_video = models.FileField(upload_to='course_videos/', blank=True, null=True, validators=[validate_video])  
    title = models.CharField(max_length=500, unique=True)
    sub_title = models.TextField()
    category = models.ForeignKey(course_category, on_delete=models.CASCADE)
    course_slug = models.SlugField(default='', max_length=500, null=True, blank=True)
    level = models.CharField(choices=level, max_length=100, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    credits = models.IntegerField(null=True, blank=True)
    is_free_course = models.BooleanField(default=False)
    overview = RichTextField(help_text="For consistency, use 'h2' for all headings and 'paragraph' formatting for text content within the Rich Text Field.")

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        first_chapter = self.course_chapter_set.first()
        if first_chapter:
            first_lesson = first_chapter.course_lesson_set.first()
            if first_lesson:
                return reverse("course_content", kwargs={'slug': self.course_slug, 'lesson_slug': first_lesson.slug})
        return reverse("course_content", kwargs={'slug': self.course_slug, 'lesson_slug': None})

class course_FAQ(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=5000)
    def __str__(self) -> str:
        return self.question

def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    model = instance.__class__
    res = model.objects.filter(slug=slug).order_by('-id')
    if res.exists():
        new_slug = f"{slug}-{res.first().id}"
        return create_slug(instance, new_slug=new_slug)
    return slug

def create_course_slug(instance, new_slug=None):
    course_slug = slugify(instance.title)
    if new_slug is not None:
        course_slug = new_slug
    model = instance.__class__
    res = model.objects.filter(course_slug=course_slug).order_by('-id')
    exists = res.exists()
    if exists:
        new_slug = "%s-%s" % (course_slug, res.first().id)
        return create_course_slug(instance, new_slug=new_slug)
    return course_slug

def pre_save_post_course_receiver(sender, instance, *args, **kwargs):
    if not instance.course_slug:
        instance.course_slug = create_course_slug(instance)
pre_save.connect(pre_save_post_course_receiver, Courses)

class course_Chapter(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    def __str__(self):
        return self.title

validate_video_extension = partial(validate_file_extension, allowed_extensions=['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'])

from urllib.parse import urlparse, parse_qs

class course_Lesson(models.Model):
    chapter = models.ForeignKey(course_Chapter, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_upload = models.FileField(upload_to='course_videos', blank=True, null=True, validators=[validate_video_extension])
    video_url = models.URLField(max_length=500, blank=True, null=True)
    duration = models.DurationField(default=timedelta(seconds=0))
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_content", kwargs={'slug': self.chapter.course.course_slug, 'lesson_slug': self.slug})

    def get_next_lesson(self):
        return self.chapter.course_lesson_set.filter(id__gt=self.id).first()

    def get_previous_lesson(self):
        return self.chapter.course_lesson_set.filter(id__lt=self.id).last()

    def save(self, *args, **kwargs):
        if self.video_url:
            parsed_url = urlparse(self.video_url)
            if "youtu.be" in parsed_url.netloc:
                video_id = parsed_url.path.lstrip("/")
                self.video_url = f"https://www.youtube.com/embed/{video_id}"
            elif "youtube.com" in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                video_id = query_params.get("v", [None])[0]
                if video_id:
                    self.video_url = f"https://www.youtube.com/embed/{video_id}"
        super().save(*args, **kwargs)

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)
pre_save.connect(pre_save_post_receiver, course_Lesson)

class Payment(models.Model):
    order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    course = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} -- {self.course.title}"
