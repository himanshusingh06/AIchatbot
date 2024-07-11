from django.urls import path
from . import views
urlpatterns = [
    path('chatbot', views.chatbot, name='chatbot'),
    path('', views.home, name='home'),
    path('login',views.login,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout,name='logout'),
    path('contact',views.contact,name='contact'),
    path('subscribe_to_pro', views.subscribe_to_pro, name='subscribe_to_pro'),
]
