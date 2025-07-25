import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from vt_site.models import Plan
from django.core.exceptions import ValidationError
from functools import partial
import os
import mimetypes
import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from vt_site.models import Plan
from django.core.exceptions import ValidationError
from functools import partial
from django.conf import settings
from django.contrib.auth import get_user_model

def upload_to_profile_pics(instance, filename):
    return f"profile_pics/{instance.user.id}/{filename}"

def validate_file_extension_and_mime(file, allowed_extensions, allowed_mime_types):
    """Validate file extension and MIME type"""
    try:
        if file.name.count('.') > 1:
            raise ValidationError("File has multiple extensions. Only one extension is allowed.")

        # file extension
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(f"Unsupported file extension. Allowed extensions are: {', '.join(allowed_extensions)}")

        # MIME type
        mime_type, _ = mimetypes.guess_type(file.name)
        if mime_type not in allowed_mime_types:
            raise ValidationError(f"Unsupported file type. Allowed types are: {', '.join(allowed_mime_types)}")
    except Exception as e:
        raise ValidationError(f"File validation failed: {str(e)}")

validate_image = partial(
    validate_file_extension_and_mime,
    allowed_extensions=['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    allowed_mime_types=['image/jpeg', 'image/png', 'image/gif', 'image/bmp']
)

# class User(AbstractUser):
#     username = models.CharField(max_length=500, blank=True, null=True)
#     mobile = PhoneNumberField(unique=True, verbose_name="Mobile Number")
#     otp = models.CharField(max_length=100,null=True,blank=True)
#     password_reset_sent_at = models.DateTimeField(null=True, blank=True)
#     reset_link_valid = models.BooleanField(default=False)
#     pic = models.ImageField(upload_to='media/profile_pics',null=True, blank=True, validators=[validate_image])
#     current_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, blank=True, null=True)
#     coins = models.IntegerField(null=True,blank=True, default=100)
#     feedback_last_sent_at = models.DateTimeField(null=True, blank=True)

#     browser = models.CharField(max_length=100, blank=True, null=True)
#     os = models.CharField(max_length=100, blank=True, null=True)
#     ip_address = models.GenericIPAddressField(null=True, blank=True)

#     USERNAME_FIELD = "mobile"
#     REQUIRED_FIELDS = ["username","email"]


#     def __str__(self):
#         return str(self.mobile)
class User(AbstractUser):
    username = models.CharField(max_length=500, blank=True, null=True)
    mobile = PhoneNumberField(unique=True, verbose_name="Mobile Number")
    otp = models.CharField(max_length=100,null=True,blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)
    reset_link_valid = models.BooleanField(default=False)
    pic = models.ImageField(upload_to='media/profile_pics',null=True, blank=True, validators=[validate_image])
    current_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, blank=True, null=True)
    coins = models.IntegerField(null=True,blank=True, default=100)
    feedback_last_sent_at = models.DateTimeField(null=True, blank=True)

    browser = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = ["username","email"]

    def __str__(self):
        return str(self.mobile)

class account_FAQ_cate(models.Model):
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class account_FAQ(models.Model):
    category = models.ForeignKey(account_FAQ_cate, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=5000)

    def __str__(self) -> str:
        return self.question

class LoginActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    browser = models.CharField(max_length=200)
    os = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.ip_address} | {self.browser} | {self.os}"
    
User = get_user_model()

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.count}"
    
User = get_user_model()

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"