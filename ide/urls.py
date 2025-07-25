from django.urls import path
from .views import *

urlpatterns = [
    path('', editor_view, name='ide'),
]
