# inkwell/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('indexNotifications', views.indexNotifications, name='indexNotifications'),
    path('indexDiscoverAuthors', views.indexDiscoverAuthors, name='indexDiscoverAuthors'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('settings', views.settings, name='settings'),
    path('password_change', views.password_change, name='password_change'),
    path('username_change', views.username_change, name='username_change'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('ink_settings', views.ink_settings, {'inkQuery':''}, name='ink_settings'),
    path('ink_settings/<str:inkQuery>', views.ink_settings, name='ink_settings'),
    path('searchInkSettings', views.searchInkSettings, name='searchInkSettings'),
    path('privatizeInk/<int:inkid>/<str:command>', views.privatizeInk, name='privatizeInk'),
    path('delete_ink/<int:inkID>', views.delete_ink, name='delete_ink'),
    path('newInk', views.newInk, name='newInk'),
    path('<int:inkID>/checkNewInkTitle', views.checkNewInkTitle, name='checkNewInkTitle'),
    path('checkNewUsername', views.checkNewUsername, name='checkNewUsername'),
    path('edit_ink/<int:inkID>/checkNewInkTitle', views.checkNewInkTitle, name='checkNewInkTitle'),
    path('edit_ink/<int:inkID>', views.edit_ink, name='edit_ink'),
    path('addNewChapter/<int:newChapterNumber>/<int:inkId>', views.addNewChapter, name='addNewChapter'),
    path('edit_chapter/<int:chapterID>/<int:inkID>', views.edit_chapter, name='edit_chapter'),
    path('yourCoAuthorRequests', views.yourCoAuthorRequests, {'searchQuery':''}, name='yourCoAuthorRequests'),
    path('yourCoAuthorRequests/<str:searchQuery>', views.yourCoAuthorRequests, name='yourCoAuthorRequests'),
    path('searchYourCoAuthorRequests', views.searchYourCoAuthorRequests, name='searchYourCoAuthorRequests'),
    path('coAuthorRequestsList', views.coAuthorRequestsList, {'searchQuery':''}, name='coAuthorRequestsList'),
    path('coAuthorRequestsList/<str:searchQuery>', views.coAuthorRequestsList, name='coAuthorRequestsList'),
    path('searchCoAuthorRequestsList', views.searchCoAuthorRequestsList, name='searchCoAuthorRequestsList'),
    path('coAuthorRequest/<int:chapterID>/<int:requestID>', views.coAuthorRequest, name='coAuthorRequest'),
    path('ink_view/<int:inkID>', views.ink_view, name='ink_view'),
    path('ink_view/<int:inkID>/followInk', views.followInk, name='followInk'),
    path('ink_view/<int:inkID>/unfollowInk', views.unfollowInk, name='unfollowInk'),
    path('ink_view/deleteComment/<int:commentID>', views.deleteComment, name='deleteComment'),
    path('inkCoAuthors/<int:inkID>', views.inkCoAuthors, {'searchQuery':''}, name='inkCoAuthors'),
    path('inkCoAuthors/<int:inkID>/<str:searchQuery>', views.inkCoAuthors, name='inkCoAuthors'),
    path('searchInkCoAuthors/<int:inkID>', views.searchInkCoAuthors, name='searchInkCoAuthors'),
    path('well/<str:username>', views.well, name='well'),
    path('well/<str:username>/followers', views.followers, {'searchQuery':''}, name='followers'),
    path('well/<str:username>/followers/<str:searchQuery>', views.followers, name='followers'),
    path('searchFollowers/<str:username>', views.searchFollowers, name='searchFollowers'),
    path('well/<str:username>/coauthors', views.coauthors, {'searchQuery':''}, name='coauthors'),
    path('well/<str:username>/coauthors/<str:searchQuery>', views.coauthors, name='coauthors'),
    path('searchCoAuthors/<str:username>', views.searchCoAuthors, name='searchCoAuthors'),
    path('timeline/<int:page>', views.timeline, name='timeline'),
    path('notifications/<int:page>', views.notifications, name='notificaitons'),
    path('well/<str:username>/follow', views.follow, name='follow'),
    path('well/<str:username>/unfollow', views.unfollow, name='unfollow'),
    path('mainSearch', views.mainSearch, name='mainSearch'),
    path('mainSearchResults/<str:searchQuery>/', views.mainSearchResults, name='mainSearchResults')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)