from django.contrib import admin

from .models import Ink, Notification, Well, CoAuthor, Follow

# Register your models here.
admin.site.register(Well)
admin.site.register(Ink)
admin.site.register(Notification)
admin.site.register(CoAuthor)
admin.site.register(Follow)
