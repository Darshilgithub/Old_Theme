from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from functools import partial
import os

def validate_file_extension(file, allowed_extensions):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"Unsupported file extension. Allowed extensions are: {', '.join(allowed_extensions)}")

validate_image = partial(validate_file_extension, allowed_extensions=['.jpg', '.jpeg', '.png', '.gif', '.bmp'])


class tutorial_category(models.Model):
    icon = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=500, null=True)
    image = models.ImageField(upload_to='media/tutorial_category', null=True, validators=[validate_image])

    def __str__(self) -> str:
        return self.name

class Tutorial(models.Model):
    status = (
        ('upcoming', 'upcoming'),
        ('trending', 'trending'),
        ('none', 'none')
    )
    image = models.ImageField(upload_to='media/tutorial_imgs', null=True, validators=[validate_image])
    title = models.CharField(max_length=500)
    category = models.ForeignKey(tutorial_category,on_delete=models.CASCADE)
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)
    status = models.CharField(choices=status,max_length=100,null=True)

    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        first_lesson = tutorials_Lesson.objects.filter(chapter__tutorial=self).first()
        if first_lesson:
            return reverse("tutorial_content", kwargs={'slug': self.slug, 'lesson_slug': first_lesson.slug})
        return reverse("tutorial_content", kwargs={'slug': self.slug, 'lesson_slug': None})


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    model = instance.__class__ 
    res = model.objects.filter(slug=slug).order_by('-id')
    exists = res.exists()
    if exists:
        new_slug = "%s-%s" % (slug, res.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, Tutorial)


class tutorial_Chapter(models.Model):
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class tutorials_Lesson(models.Model):
    chapter = models.ForeignKey(tutorial_Chapter, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = RichTextField(help_text="For consistency, use 'h2' for all headings and 'paragraph' formatting for text content within the Rich Text Field.")
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("tutorial_content", kwargs={'slug': self.chapter.tutorial.slug, 'lesson_slug': self.slug})
    
    def get_next_lesson(self):
        next_lesson = self.chapter.tutorials_lesson_set.filter(id__gt=self.id).first()
        return next_lesson

    def get_previous_lesson(self):
        previous_lesson = self.chapter.tutorials_lesson_set.filter(id__lt=self.id).last()
        return previous_lesson
    
pre_save.connect(pre_save_post_receiver, tutorials_Lesson)

