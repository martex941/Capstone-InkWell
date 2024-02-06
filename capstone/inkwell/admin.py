from django.contrib import admin

from .models import Ink, Notification, Well, Follow, User, Chapter, Post, Comment, CoAuthorRequest, DiscoverAuthors, Tag, UpdateAuthorsDate

# Register your models here.
admin.site.register(User)
admin.site.register(Well)
admin.site.register(Ink)
admin.site.register(Chapter)
admin.site.register(Post)
admin.site.register(Notification)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(CoAuthorRequest)
admin.site.register(DiscoverAuthors)
admin.site.register(Tag)
admin.site.register(UpdateAuthorsDate)