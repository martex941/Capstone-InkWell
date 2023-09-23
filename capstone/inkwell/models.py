from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

class User(AbstractUser):
    followers = models.PositiveIntegerField(default=0)
    coAuthorRequests = models.PositiveIntegerField(default=0)
    acceptedRequests = models.PositiveIntegerField(default=0)

    @property
    def readers(self):
        r = Ink.objects.filter(inkOwner=self).values_list('views', flat=True)
        r = sum(r)
        return r
    
    @property
    def letters(self):
        l = Ink.objects.filter(inkOwner=self).values_list('letterCount', flat=True)
        l = sum(l)
        return l
    

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
    coAuthors = models.ManyToManyField("CoAuthor")
    privateStatus = models.BooleanField(default=False)
    updateStatus = models.BooleanField(default=False) # If the Ink is edited at least once, this changes to true
    following = models.ManyToManyField(User)
    genre = models.CharField(max_length=64, default="")
    description = models.CharField(max_length=500, default="")
    title = models.CharField(max_length=64, default="")
    content = models.TextField()
    views = models.PositiveBigIntegerField(default=0)
    letterCount = models.PositiveBigIntegerField(default=0)
    creation_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.title} by {self.inkOwner}"
    
class InkVersionControl(models.Model):
    comment = models.CharField(max_length=120, default="")
    originalInk = models.ForeignKey(Ink, on_delete=models.CASCADE)
    contents = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
class CoAuthor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="CoAuthor", default="")
    
class Notification(models.Model):
    notifiedUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifiedUser", default="")
    contents = models.CharField(max_length=120, default="")
    date = models.DateTimeField(default=timezone.now, editable=False)
    url = models.CharField(max_length=120, default="")
