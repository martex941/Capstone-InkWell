from django.contrib import admin

from .models import Ink, Notification, Well

# Register your models here.
admin.site.register(Well)
admin.site.register(Ink)
admin.site.register(Notification)
