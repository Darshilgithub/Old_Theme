# Generated by Django 5.0.6 on 2025-01-23 16:12

import functools
import vt_site.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vt_site', '0018_alter_site_detail_circle_animation_image_1_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(upload_to='media/top_categories', validators=[functools.partial(vt_site.models.validate_file_extension, *(), **{'allowed_extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp']})])),
                ('slug', models.SlugField(blank=True, default='', max_length=500, null=True)),
            ],
        ),
    ]
