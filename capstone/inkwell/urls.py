# inkwell/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('settings', views.settings, name='settings'),
    path('password_change', views.password_change, name='password_change'),
    path('username_change', views.username_change, name='username_change'),
    path('ink_settings', views.ink_settings, name='ink_settings'),
    path('newInk', views.newInk, name='newInk'),
    path('ink_view', views.ink_view, name='ink_view'),
    path('well/<str:username>', views.well, name="well"),
    path('well/<str:username>/followers', views.followers, name='followers'),
    path('well/<str:username>/coauthors', views.coauthors, name='coauthors'),
    path('timeline/<int:page>', views.timeline, name='timeline'),
    path('notifications/<int:page>', views.notifications, name='notificaitons')
]
