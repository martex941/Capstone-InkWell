from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

class User(AbstractUser):
    pass

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower", default="")
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followee", default="")

class Well(models.Model):
    wellOwner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="well_owner", default="")
    privateStatus = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.wellOwner}'s well"
    
class Ink(models.Model):
    wellOrigin = models.ForeignKey(Well, on_delete=models.CASCADE, related_name="well_pk", default="")
    inkOwner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ink_owner", default="")
    coAuthor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="co_author", default="")
    privateStatus = models.BooleanField(default=False)
    genre = models.CharField(max_length=64, default="")
    title = models.CharField(max_length=64, default="")
    content = models.TextField()
    creation_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.title} by {self.inkOwner}"
    
class CoAuthor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="CoAuthor", default="")
    ink = models.ForeignKey(Ink, on_delete=models.CASCADE, related_name="co_ink", default="")

    def __str__(self):
        return f"{self.user}'s contribution to {self.ink}"
    
class Notification(models.Model):
    notifiedUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifiedUser", default="")
    contents = models.CharField(max_length=120, default="")
    date = models.DateTimeField(default=timezone.now, editable=False)
    url = models.CharField(max_length=120, default="")
