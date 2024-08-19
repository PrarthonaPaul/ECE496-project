from django.urls import path  #path is used to define url patterns
from django.contrib.auth import views as auth_views # django's inbuilt authentication module which has views like Login-view
from . import views #imports views from file_processor

urlpatterns = [
    path ('login/', auth_views.LoginView.as_view(template_name = 'login.html'),name='login'), #sets up the login url, using the standard LoginView template to serve the login page
    path('register/',views.register, name='register') #sets up the registration url
]

