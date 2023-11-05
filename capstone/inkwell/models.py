from django.contrib.auth.models import AbstractUser
from django_quill.fields import QuillField
from django.utils import timezone
from django.db import models

class User(AbstractUser):
    about = models.CharField(max_length=250, default="")
    profilePicture = models.ImageField(upload_to='', blank=True, null=True)

    coAuthorRequests = models.PositiveIntegerField(default=0)

    @property
    def acceptedCoAuthorRequests(self):
        acar = Ink.objects.filter(inkOwner=self).values_list('coAuthors', flat=True)
        return acar.count()

    @property
    def followers(self):
        f = Follow.objects.filter(followee=self)
        return f.count()
    
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
    
    def __str__(self):
        return f"{self.username}"
    

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower", default="")
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followee", default="")

    def __str__(self):
        return f"{self.follower} follows {self.followee}"

class Well(models.Model):
    wellOwner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="well_owner", default="")
    privateStatus = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.wellOwner}'s well"

class Ink(models.Model):
    wellOrigin = models.ForeignKey(Well, on_delete=models.CASCADE, related_name="well_pk", default="")
    inkOwner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ink_owner", default="")
    coAuthors = models.ManyToManyField(User, related_name="CoAuthors",blank=True)
    privateStatus = models.BooleanField(default=False)
    updateStatus = models.BooleanField(default=False) # If the Ink is edited at least once, this changes to true
    ink_following = models.ManyToManyField(User, related_name="ink_following",blank=True)
    genre = models.CharField(max_length=64, default="")
    description = models.CharField(max_length=500, default="")
    title = models.CharField(max_length=64, default="")
    content = models.TextField()
    views = models.PositiveBigIntegerField(default=0)
    letterCount = models.PositiveBigIntegerField(default=0)
    creation_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.title} by {self.inkOwner}"
    
class Chapter(models.Model):
    chapterNumber = models.PositiveIntegerField(default=1)
    chapterTitle = models.CharField(max_length=64)
    chapterContents = QuillField()
    chapterInkOrigin = models.ForeignKey(Ink, on_delete=models.CASCADE, related_name="chapterInkOrigin", default="")

    def __str__(self):
        return f"Chapter {self.chapterNumber} of {self.chapterInkOrigin.title} titled {self.chapterTitle}"
    
class Notification(models.Model):
    notifiedUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifiedUser", default="")
    contents = models.CharField(max_length=120, default="")
    date = models.DateTimeField(default=timezone.now, editable=False)
    url = models.CharField(max_length=120, default="")

class Post(models.Model):
    message = models.TextField()
    referencedPostInk = models.ForeignKey(Ink, on_delete=models.CASCADE, related_name="referencedPostInk", default="")
    postCreationDate = models.DateTimeField(default=timezone.now, editable=False)

class Comment(models.Model):
    content = models.TextField()
    commentInkOrigin = models.ForeignKey(Ink, on_delete=models.CASCADE, related_name="commentInkOrigin", default="")
    commentAuthor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentAuthor", default="")
    commentCreationDate = models.DateTimeField(default=timezone.now, editable=False)

class CoAuthorRequest(models.Model):
    coAuthor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coAuthor", default="")
    requestedChapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="requestedChapter", default="")
    requestedContentChange = QuillField()
    requestDate = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.coAuthor} is requesting to edit {self.requestedChapter}"
