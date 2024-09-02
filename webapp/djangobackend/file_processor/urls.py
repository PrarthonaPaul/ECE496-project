from django.urls import path  #path is used to define url patterns
from django.contrib.auth import views as auth_views # django's inbuilt authentication module which has views like Login-view
from . import views #imports views from file_processor

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('login/', views.login_view, name='login'),  # Add the login URL here
]

