
from django.conf import settings
from django.urls import include, path
from . import views
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('contactUs', views.contact, name='contact'),
    path('plans', views.plans, name='plans'),
    path('maintenance', views.maintenance, name='maintenance'),
    path('faq', views.faq, name='faq'),
    path('terms_pages/<slug:slug>', views.privacy, name='terms_pages'),
    path('tutorial/', include('tutorial.urls')),
    path('courses/', include('video_courses.urls')),
    path('accounts/', include('account.urls')),
    path('compiler/', include('ide.urls'), name='ide'),
    path('dashboard/', views.my_dashboard, name='my_dashboard'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


