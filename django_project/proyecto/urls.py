from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='index'),
    path('page_1/', views.page_1, name='page_1'),
    path('page_2/', views.page_2, name='page_2'),
    path('page_3/', views.page_3, name='page_3'),
]
