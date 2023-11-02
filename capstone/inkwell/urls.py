# inkwell/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('settings', views.settings, name='settings'),
    path('password_change', views.password_change, name='password_change'),
    path('username_change', views.username_change, name='username_change'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('ink_settings', views.ink_settings, name='ink_settings'),
    path('newInk', views.newInk, name='newInk'),
    path('<int:inkID>/checkNewInkTitle', views.checkNewInkTitle, name='checkNewInkTitle'),
    path('edit_ink/<int:inkID>/checkNewInkTitle', views.checkNewInkTitle, name='checkNewInkTitle'),
    path('edit_ink/<int:inkID>', views.edit_ink, name='edit_ink'),
    path('addNewChapter/<int:newChapterNumber>/<int:inkId>', views.addNewChapter, name='addNewChapter'),
    path('edit_chapter/<int:chapterID>/<int:inkID>', views.edit_chapter, name='edit_chapter'),
    path('ink_view/<int:inkID>', views.ink_view, name='ink_view'),
    path('ink_view/<int:inkID>/followInk', views.followInk, name='followInk'),
    path('ink_view/<int:inkID>/unfollowInk', views.unfollowInk, name='unfollowInk'),
    path('well/<str:username>', views.well, name="well"),
    path('well/<str:username>/followers', views.followers, name='followers'),
    path('well/<str:username>/coauthors', views.coauthors, name='coauthors'),
    path('timeline/<int:page>', views.timeline, name='timeline'),
    path('notifications/<int:page>', views.notifications, name='notificaitons'),
    path('well/<str:username>/follow', views.follow, name='follow'),
    path('well/<str:username>/unfollow', views.unfollow, name='unfollow')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)