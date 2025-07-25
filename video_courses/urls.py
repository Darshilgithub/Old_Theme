from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import get_lessons 

urlpatterns = [
    path('', views.courses, name='courses'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('stream_video/<slug:lesson_slug>/', views.stream_video, name='stream_video'),
    path('<slug:slug>/<slug:lesson_slug>/', views.course_content, name='course_content'),
    path('verify_payment', views.verify_payment, name='payment_verification'),
    path('my_courses', views.my_courses, name='my_courses'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
