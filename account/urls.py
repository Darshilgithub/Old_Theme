from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import logout_view

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('verify_account/', views.otpVerify, name='verify_otp'),
    path('reset_password', views.CustomPasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent', auth_views.PasswordResetDoneView.as_view(template_name='registration/Passreset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete', auth_views.PasswordResetCompleteView.as_view(template_name='registration/Passreset_done.html'), name='password_reset_complete'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('profile', views.profile, name='profile'),
    path('view_profile', views.profile_view, name="view_profile"),
    path('edit_profile', views.profile_edit, name="edit_profile"),
    path('settings', views.settings, name="settings"),
    path('settings/account_info', views.account_info, name="account_info"),
    path('settings/account_info/delete_account', views.delete_account, name="delete_account"),
    path('settings/update_mobile', views.mobileChange, name="mobileChange"),
    path('settings/update_email', views.emailChange, name="emailChange"),
    path('settings/change_password', views.CustomPasswordChangeView.as_view(), name="passChange"),
    path('settings/support', views.support, name="support"),
    path('logout/', logout_view, name='logout'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
