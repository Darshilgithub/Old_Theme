from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import pre_save
from colorfield.fields import ColorField
from phonenumbers import PhoneNumber
from django.core.exceptions import ValidationError
from functools import partial
import os
from django.contrib.auth import get_user_model

from django.conf import settings
def validate_file_extension(file, allowed_extensions):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"Unsupported file extension. Allowed extensions are: {', '.join(allowed_extensions)}")

validate_image = partial(validate_file_extension, allowed_extensions=['.jpg', '.jpeg', '.png', '.gif', '.bmp'])

class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    color = ColorField(default='#09c4ff')
    background_color = ColorField(default='#313b44db')

    def __str__(self):
        return self.name

class Accepted_points(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    points = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.plan.name} - {self.points}"

class Normal_points(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    points = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.plan.name} - {self.points}"

class NotAccepted_points(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    points = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.plan.name} - {self.points}"

class Terms_pages(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    content = RichTextField(help_text="For consistency, use 'h2' for all headings and 'paragraph' formatting for text content within the Rich Text Field.")
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("terms_pages", kwargs={'slug': self.slug})

    def __str__(self) -> str:
        return self.name

def create_slug(instance, new_slug=None):
    slug = slugify(instance.name)
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

pre_save.connect(pre_save_post_receiver, Terms_pages)

class Teammate(models.Model):
    pic = models.ImageField(upload_to='media/teammates', null=True, blank=True, validators=[validate_image])
    name = models.CharField(max_length=300)
    role = models.CharField(max_length=500)
    insta_link = models.CharField(max_length=200, null=True, blank=True)
    linkedin_link = models.CharField(max_length=200, null=True, blank=True)
    email_id = models.EmailField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

class teammate_skills(models.Model):
    teammate = models.ForeignKey(Teammate, on_delete=models.CASCADE)
    skill = models.CharField(max_length=100)

class site_detail(models.Model):
    home_page_title = models.CharField(max_length=100)
    home_page_desc = models.CharField(max_length=200, blank=True, null=True)
    footer_desc = models.CharField(max_length=500)
    copyright_year = models.CharField(max_length=4)
    contact_mail = models.EmailField()
    contact_number = PhoneNumber()

    circle_animation_image_1 = models.ImageField(upload_to='media/circle_animation', null=True, validators=[validate_image])
    circle_animation_image_2 = models.ImageField(upload_to='media/circle_animation', null=True, validators=[validate_image])
    circle_animation_image_3 = models.ImageField(upload_to='media/circle_animation', null=True, validators=[validate_image])
    circle_animation_image_4 = models.ImageField(upload_to='media/circle_animation', null=True, validators=[validate_image])
    circle_animation_image_5 = models.ImageField(upload_to='media/circle_animation', null=True, validators=[validate_image])
    circle_animation_image_6 = models.ImageField(upload_to='media/circle_animation', null=True, validators=[validate_image])

    def split_text(self):
        return self.home_page_title.split(" ")
    
    def __str__(self) -> str:
        return self.home_page_title

class site_details_links(models.Model):
    name = models.ForeignKey(site_detail, on_delete=models.CASCADE)
    icon = models.CharField(max_length=100)
    link = models.CharField(max_length=200)

class FAQ_cate(models.Model):
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class FAQ(models.Model):
    category = models.ForeignKey(FAQ_cate, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=5000)

    def __str__(self) -> str:
        return self.question

class TopCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='media/top_categories', validators=[validate_image])
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("top_category_detail", kwargs={'slug': self.slug})

pre_save.connect(pre_save_post_receiver, TopCategory)
class LoginActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='site_login_activities')
    ip = models.GenericIPAddressField()
    browser = models.CharField(max_length=200)
    os = models.CharField(max_length=200)
    device = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.ip} - {self.browser} on {self.os}"
