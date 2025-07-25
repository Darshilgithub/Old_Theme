from django.contrib import admin

from vt_site.models import *

class Accepted_points_TabularInline(admin.TabularInline):
    model = Accepted_points

class Normal_points_TabularInline(admin.TabularInline):
    model = Normal_points

class NotAccepted_points_TabularInline(admin.TabularInline):
    model = NotAccepted_points

class plan_admin(admin.ModelAdmin):
    inlines = (Accepted_points_TabularInline, Normal_points_TabularInline, NotAccepted_points_TabularInline)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save() 

class TeammateSkills_TabularInline(admin.TabularInline):
    model = teammate_skills

class Teammate_skills_admin(admin.ModelAdmin):
    inlines = [TeammateSkills_TabularInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save() 

class site_links_TabularInline(admin.TabularInline):
    model = site_details_links

class site_links_admin(admin.ModelAdmin):
    inlines = [site_links_TabularInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save()

class FAQ_TabularInline(admin.TabularInline):
    model =  FAQ

class FAQ_admin(admin.ModelAdmin):
    inlines = [ FAQ_TabularInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save() 

admin.site.register(FAQ_cate,  FAQ_admin)
admin.site.register(Plan, plan_admin)
admin.site.register(Terms_pages)
admin.site.register(Teammate,Teammate_skills_admin)
admin.site.register(site_detail,site_links_admin)