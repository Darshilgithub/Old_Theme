# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth import get_user_model
# from account.models import account_FAQ, account_FAQ_cate


# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'first_name', 'last_name', 'email', 'mobile', 'is_superuser')
#     list_filter = ('is_staff', 'is_superuser', 'groups')
#     search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal Info', {'fields': ('pic', 'first_name', 'last_name', 'email', 'mobile', 'current_plan', 'coins', 'otp', 'password_reset_sent_at', 'feedback_last_sent_at', 'reset_link_valid')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('pic', 'username', 'email', 'first_name', 'last_name', 'mobile', 'password1', 'password2'),
#         }),
#     )

# class account_FAQ_TabularInline(admin.TabularInline):
#     model = account_FAQ

# class account_FAQ_admin(admin.ModelAdmin):
#     inlines = [account_FAQ_TabularInline]

#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         if '_addanother' not in request.POST:
#             obj.save() 

# admin.site.register(account_FAQ_cate, account_FAQ_admin)
# admin.site.register(get_user_model(), CustomUserAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from account.models import account_FAQ, account_FAQ_cate
from .models import LoginActivity
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email', 'mobile',
        'browser', 'os', 'ip_address',  # ✅ Add these fields
        'is_superuser'
    )
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        # ('Personal Info', {
        #     'fields': (
        #         'pic', 'first_name', 'last_name', 'email', 'mobile',
        #         'current_plan', 'coins', 'otp',
        #         'password_reset_sent_at', 'feedback_last_sent_at', 'reset_link_valid',
        #         'browser', 'os', 'device'  # ✅ Add here too
        #     )
        # }),
        ('Personal Info', {
            'fields': (
                'pic', 'first_name', 'last_name', 'email', 'mobile',
                'current_plan', 'coins', 'otp', 'password_reset_sent_at',
                'feedback_last_sent_at', 'reset_link_valid',
                'browser', 'os', 'ip_address'  # ✅ Must be included here too
            )
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'pic', 'username', 'email', 'first_name', 'last_name', 'mobile',
                'password1', 'password2'
            ),
        }),
    )

class account_FAQ_TabularInline(admin.TabularInline):
    model = account_FAQ

class account_FAQ_admin(admin.ModelAdmin):
    inlines = [account_FAQ_TabularInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if '_addanother' not in request.POST:
            obj.save() 

admin.site.register(account_FAQ_cate, account_FAQ_admin)
admin.site.register(get_user_model(), CustomUserAdmin)

@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'browser', 'os', 'timestamp')
    search_fields = ('user__username', 'ip_address', 'browser', 'os')
    list_filter = ('timestamp',)