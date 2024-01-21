from django.contrib.auth.models import AbstractUser
from django_quill.fields import QuillField
from django.utils import timezone
from collections import Counter
from django.db import models

class User(AbstractUser):
    about = models.CharField(max_length=250, default="")
    profilePicture = models.ImageField(upload_to='', blank=True, null=True)


    @property
    def mostUsedTags(self):
        tags = Ink.objects.filter(inkOwner=self).exclude(tags=None).values_list('tags', flat=True)
        tagCounter = Counter(tags)
        most_common = tagCounter.most_common(3)
        most_common_tag_ids = [tag[0] for tag in most_common]
        t = Tag.objects.filter(id__in=most_common_tag_ids)
        return t

    @property
    def yourCoAuthorRequests(self): # Amount of co-author requests the author made to other inks
        ycar = CoAuthorRequest.objects.filter(coAuthor=self)
        return ycar.count()

    @property
    def yourAcceptedCoAuthorRequests(self):# Amount of co-author requests the author made to other inks that were accepted
        yacar = Ink.objects.filter(coAuthors=self)
        return yacar.count()

    @property
    def acceptedCoAuthorRequests(self): # Amount of accepted co-author requests the author got from other authors
        acar = Ink.objects.filter(inkOwner=self).exclude(coAuthors=None).values_list('coAuthors', flat=True)
        return acar.count()
    
    @property
    def collaborators(self):
        collabs = Ink.objects.filter(inkOwner=self).exclude(coAuthors=None).values_list('coAuthors', flat=True)
        return collabs

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
        inks = Ink.objects.filter(inkOwner=self)
        allChapters = Chapter.objects.filter(chapterInkOrigin__in=inks)
        total_letter_count = 0
    
        for chapter in allChapters:
            letter_count = len([char for char in chapter.chapterContents.html if char.isalpha()])
            total_letter_count += letter_count

        return total_letter_count
    
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

class Tag(models.Model):
    tagName = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.tagName}"

class Ink(models.Model):
    wellOrigin = models.ForeignKey(Well, on_delete=models.CASCADE, related_name="well_pk", default="")
    inkOwner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ink_owner", default="")
    coAuthors = models.ManyToManyField(User, related_name="CoAuthors", blank=True)
    privateStatus = models.BooleanField(default=False)
    updateStatus = models.BooleanField(default=False) # If the Ink is edited at least once, this changes to true
    ink_following = models.ManyToManyField(User, related_name="ink_following", blank=True)
    tags = models.ManyToManyField(Tag, related_name="tags", blank=True)
    description = models.CharField(max_length=500, default="")
    title = models.CharField(max_length=64, default="")
    views = models.PositiveBigIntegerField(default=0)
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
    coAuthor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coAuthor", default="") # Person who made the request
    requestedChapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="requestedChapter", default="")
    chapterContents = QuillField()
    requestDate = models.DateTimeField(default=timezone.now, editable=False)
    acceptedStatus = models.BooleanField(default=False)
    declinedMessage = models.TextField(default="")

    def __str__(self):
        return f"{self.coAuthor} is requesting to edit {self.requestedChapter}"

class DiscoverAuthors(models.Model):
    popularAuthors = models.ManyToManyField(User, related_name="popularAuthors", blank=True)
    topAuthors = models.ManyToManyField(User, related_name="topAuthors", blank=True)
    topCoAuthors = models.ManyToManyField(User, related_name="topCoAuthors", blank=True)
    discoverAuthors = models.ManyToManyField(User, related_name="discoverAuthors", blank=True)