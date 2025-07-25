from django.contrib import admin
from .models import *

class tutorials_Lesson_TabularInline(admin.TabularInline):
    model = tutorials_Lesson

class tutorials_Lesson_admin(admin.ModelAdmin):
    inlines = [tutorials_Lesson_TabularInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save() 

class tutorial_Chapter_TabularInline(admin.TabularInline):
    model = tutorial_Chapter

class tutorials_Chapter_admin(admin.ModelAdmin):
    inlines = [tutorial_Chapter_TabularInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save() 

admin.site.register(tutorial_category)
admin.site.register(Tutorial, tutorials_Chapter_admin)
admin.site.register(tutorial_Chapter, tutorials_Lesson_admin)