from django.contrib import admin
from .models import *

class course_FAQ_TabularInline(admin.TabularInline):
    model = course_FAQ
    extra = 1

class course_Lesson_TabularInline(admin.TabularInline):
    model = course_Lesson

class course_Lesson_admin(admin.ModelAdmin):
    inlines = [course_Lesson_TabularInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save()

class course_Chapter_TabularInline(admin.TabularInline):
    model = course_Chapter

class course_Chapter_admin(admin.ModelAdmin):
    inlines = [course_Chapter_TabularInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save()

class Courses_admin(admin.ModelAdmin):
    inlines = [course_Chapter_TabularInline, course_FAQ_TabularInline]
    # list_display = ('title', 'category', 'price', 'is_free_course', 'intro_video')
    # fields = ('title', 'sub_title', 'category', 'level', 'price', 'credits', 'is_free_course', 'overview', 'intro_video')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save()


admin.site.register(course_category)
admin.site.register(Courses, Courses_admin)
admin.site.register(course_Chapter, course_Lesson_admin)
admin.site.register(Payment)
