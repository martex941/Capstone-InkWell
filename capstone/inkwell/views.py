# inkwell/views.py
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse
from django.db import IntegrityError
from django.db.models.functions import Random
from django.core.paginator import Paginator
import time, json

from .helpers import email_validator
from .forms import ChapterForm
from .models import User, Ink, Notification, Well, Follow, Chapter, Post

def index(request):
    users = User.objects.all()
    popularAuthors = sorted(users, key=lambda user: user.readers * user.followers, reverse=True)[:10]
    topAuthors = sorted(users, key=lambda user: user.letters * user.coAuthorRequests, reverse=True)[:10]
    topCoAuthors = sorted(users, key=lambda user: user.acceptedRequests, reverse=True)[:10]
    discoverAuthors = User.objects.annotate(random_order=Random()).order_by('random_order')[:20]

    return render(request, 'inkwell/index.html', {
        'popularAuthors': popularAuthors,
        'topAuthors': topAuthors,
        'topCoAuthors': topCoAuthors,
        'discoverAuthors': discoverAuthors
    })

def timeline(request, page):

    def serializeInks(posts):
        serialized_inks = [
            {
                'postMessage': post.message,
                'id': post.referencedPostInk.id,
                'title': post.referencedPostInk.title,
                'description': post.referencedPostInk.description,
                'privateStatus': post.referencedPostInk.privateStatus,
                'updateStatus': post.referencedPostInk.updateStatus,
                'inkOwner': post.referencedPostInk.inkOwner.username,
                'coAuthors': [coauthor.username for coauthor in post.referencedPostInk.coAuthors.all()],
                'creation_date': post.postCreationDate.strftime('%Y-%m-%d %H:%M:%S')
            }
            for post in posts.page(page).object_list
        ]
        return serialized_inks

    allPosts = Post.objects.filter(referencedPostInk__privateStatus=False).order_by('-postCreationDate')
    allPostsPag = Paginator(allPosts, 20)
    allPosts_col = serializeInks(allPostsPag)

    followers = User.objects.filter(followee__follower=request.user)
    followedInks = Ink.objects.filter(Q(inkOwner__in=followers), privateStatus=False)
    followedPosts = Post.objects.filter(Q(referencedPostInk__in=followedInks)).order_by('-postCreationDate')
    followedPostsPag = Paginator(followedPosts, 20)
    followedPosts_col = serializeInks(followedPostsPag)

    index_columns = {
        'allInks': allPosts_col,
        'followedInks': followedPosts_col,
    }

    return JsonResponse(index_columns, safe=False)

def notifications(request, page):
    notifications = Notification.objects.filter(notifiedUser=request.user).order_by('-date')
    notificationsPag = Paginator(notifications, 10)
    notifications_col = [
        {
            'contents': notif.contents,
            'date': notif.date.strftime('%Y-%m-%d %H:%M:%S'),
            'url': notif.url
        }
        for notif in notificationsPag.page(page).object_list
    ]
    return JsonResponse(notifications_col, safe=False)

@login_required
def newInk(request):
    if request.method == "POST":
        title = request.POST.get("title")
        genre = request.POST.get("genre")
        privateStatus = request.POST.get("privateStatus")
        if privateStatus == "on":
            privateStatus = True
        else:
            privateStatus = False

        description = request.POST.get("description")

        current_user = User.objects.get(username=request.user)
        user_well = Well.objects.get(wellOwner=current_user.pk)

        new_ink = Ink(
            wellOrigin=user_well, 
            inkOwner=current_user, 
            privateStatus=privateStatus, 
            updateStatus=False, 
            genre=genre, 
            description=description, 
            title=title, 
            content="", 
            )
        new_ink.save()

        time.sleep(1) # 1 second pause for the server to catch up with the newly created ink

        if not privateStatus:
            new_post = Post(message=f"{new_ink.inkOwner} created a new ink", referencedPostInk=new_ink)
            new_post.save()

        time.sleep(1) # The page loads quicker than the server so it is held by 1 second for the server to catch up
        return HttpResponseRedirect(reverse("edit_ink") + f'?inkID={new_ink.id}')

    return render(request, "inkwell/newInk.html")

@login_required
def checkNewInkTitle(request):
    data = json.loads(request.body)
    title = data.get("title", "")
    try:
        inkExists = Ink.objects.get(title=title)
        if inkExists:
            messageData = {
                'message': "Title is taken.",
                'color': "red"
            }
            return JsonResponse(messageData, safe=False)
    except Ink.DoesNotExist:
        messageData = {
            'message': "Title is available.",
            'color': "green"
            }
        return JsonResponse(messageData, safe=False)

def ink_view(request, inkID):
    viewedInk = Ink.objects.get(id=inkID)
    return render(request, "inkwell/ink_view.html", {
        "ink": viewedInk
    })

@login_required
def edit_ink(request, inkID):
    editInk = Ink.objects.get(id=inkID)
    chapters = Chapter.objects.filter(chapterInkOrigin=editInk.id).order_by("chapterNumber")
    if chapters:
        lastChapter = chapters.last().chapterNumber
    else:
        lastChapter = 0

    if request.method == "POST":
        

    return render(request, "inkwell/edit_ink.html", {
        "editInk": editInk,
        "chapters": chapters,
        "newChapterNum": (lastChapter + 1),
    })

@login_required
def addNewChapter(request, newChapterNumber, inkId):
    if request.method == "POST":
        newChapterTitle = request.POST.get("newChapterTitle")
        inkOrigin = Ink.objects.get(id=inkId)
        new_chapter = Chapter(chapterNumber=newChapterNumber, chapterTitle=newChapterTitle, chapterInkOrigin=inkOrigin)
        new_chapter.save()
        time.sleep(1) # Necessary for the server to catch up making the new chapter model
        return HttpResponseRedirect(reverse("edit_chapter", kwargs={'chapterID': new_chapter.id}))
    
@login_required
def edit_chapter(request, chapterID, inkID):
    chapterInfo = Chapter.objects.get(id=chapterID)
    inkInfo = Ink.objects.get(id=inkID)
    initial_data = {
        "chapterTitle": chapterInfo.chapterTitle,
        "chapterContents": chapterInfo.chapterContents
    }
    form = ChapterForm(initial=initial_data)
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            form = ChapterForm(request.POST, instance=chapterInfo)
            form.save()
            time.sleep(1)
            if not inkInfo.privateStatus:
                new_post = Post(message=f"{inkInfo.inkOwner} updated their ink", referencedPostInk=inkInfo)
                new_post.save()
            return HttpResponseRedirect(reverse("edit_ink", kwargs={'inkID': inkID}))
        
    return render(request, "inkwell/edit_chapter.html", {
        "chapterInfo": chapterInfo,
        "inkID": inkID,
        "form": form
    })

@login_required
def well(request, username):
    wellOwner = User.objects.get(username=username)
    inks = Ink.objects.filter(inkOwner=wellOwner.pk)
    followers = wellOwner.followers
    co_authors = wellOwner.coAuthorRequests
    followCheck = False
    if User.objects.filter(followee__follower=request.user):
        followCheck = True

    return render(request, "inkwell/well.html", {
        "wellOwner": wellOwner,
        "inks": inks,
        "followers": followers,
        "ink_number": len(inks),
        "coAuthors": co_authors,
        "followCheck": followCheck
    })

@login_required
def follow(request, username):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # Get the data from javascript post request
    data = json.loads(request.body)
    body = data.get("followee", "")

    # Get the current user and user object using the obtained JSON file
    current_user = request.user
    followed_user = User.objects.get(username=body)

    # If user isn't following themselves create a new Follow object and save it
    if current_user != followed_user:
        new_follow = Follow(follower=current_user, followee=followed_user)
        new_follow.save()

    return JsonResponse({"message": "Followed"}, status=201)

@login_required
def unfollow(request, username):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get the data from javascript post request
    data = json.loads(request.body)
    body = data.get("followee", "")

    # Get the current user and user object using the obtained JSON file
    current_user = request.user
    followed_user = User.objects.get(username=body)

    # Get the Follow object and delete it, thus ending the following of one user and another
    unfollowing = Follow.objects.get(follower=current_user, followee=followed_user)
    unfollowing.delete()

    return JsonResponse({"message": "Unfollowed"}, status=201)

def followers(request, username):
    user = User.objects.get(username=username)
    followers = User.objects.filter(follower__followee=user.pk)
    # page that displays all followers of a given user after clicking on followers on a user's well profile
    return render(request, "inkwell/followers.html", {
        "followers": followers
    })

def coauthors(request, username):
    user = User.objects.get(username=username)
    userInks = Ink.objects.filter(inkOwner=user.pk)
    coauthors = User.objects.filter(CoAuthors__in=userInks).distinct()

    return render(request, "inkwell/coauthors.html", {
        "coauthors": coauthors,
        "user": user
    })

@login_required
def settings(request):
    return render(request, "inkwell/settings.html")

@login_required
def password_change(request):
    if request.method == "POST":
        # Password change
        if "change_password" in request.POST:
            old_password = request.POST.get("oldPassword_confirm")
            new_password = request.POST.get("new_password")
            new_password_confirm = request.POST.get("newPassword_confirm")
            
            user = request.user
            
            # Check if the old password matches the user's current password
            if not user.check_password(old_password):
                return render(request, "inkwell/settings.html", {
                    "message": "Incorrect old password"
                })
            
            # Check if the new password is valid
            if len(new_password) < 8:
                return render(request, "inkwell/settings.html", {
                    "message": "New password must be at least 8 characters long"
                })
            
            # Check if the new passwords match
            if new_password != new_password_confirm:
                return render(request, "inkwell/settings.html", {
                    "message": "Passwords must match"
                })

            # Update the user's password
            user.set_password(new_password)
            user.save()
            
            # Update the session to reflect the password change
            update_session_auth_hash(request, user)
            
            return render(request, "inkwell/settings.html", {
                "message": "Password changed successfully"
            })
        
    return render(request, "inkwell/password_change.html")

@login_required
def username_change(request):
    if request.method == "POST":
        # Username change
        if "change_username" in request.POST:
            old_username = request.user
            new_username = request.POST.get("new_username")
            user = request.user
            if new_username == old_username:
                return render(request, "inkwell/settings.html", {
                    "message": "New username must be different than the old username"
                })
            elif len(new_username) < 5:
                return render(request, "inkwell/settings.html", {
                    "message": "New username must be at least 5 characters long"
                })
            elif User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                return render(request, "inkwell/settings.html", {
                    "message": "Username is already taken"
                })
        else:
            current_user = User.objects.get(pk=user.pk)
            current_user.username = new_username
            current_user.save()
            return render(request, "inkwell/settings.html", {
                "message": "Username successfully changed"
            })
        
    return render(request, "inkwell/username_change.html")

@login_required
def edit_profile(request):
    user = request.user
    current_user = User.objects.get(pk=user.pk)
    profilePic = current_user.profilePicture
    if not profilePic:
        profilePic = "no-profile-picture-icon.jpg"
    description = current_user.about

    if request.method == "POST" and "new_profile_picture" in request.FILES:
        newProfilePic = request.FILES.get("new_profile_picture")
        current_user.profilePicture = newProfilePic
        current_user.save()
        profilePic = newProfilePic
    elif request.method == "POST" and "new_description" in request.POST:
        newDescription = request.POST.get("new_description")
        current_user.about = newDescription
        current_user.save()
        description = newDescription


    return render(request, "inkwell/edit_profile.html", {
        "profile_picture": profilePic,
        "description": description
    })

@login_required
def ink_settings(request):
    retrieve_inks = Ink.objects.filter(inkOwner=request.user)
    return render(request, "inkwell/ink_settings.html", {
        "inks": retrieve_inks
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "inkwell/login.html", {
                "message": "Invalid username and/or password."
            })

    return render(request, 'inkwell/login.html')

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":

        # Necessary variables
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmedPassword = request.POST.get("confirmation")

        # Check various conditions 
        if len(username) < 5:
            return render(request, "inkwell/register.html", {
                "message": "Username must be at least 5 characters long"
            })
        
        if email_validator(email) == False:
            return render(request, "inkwell/register.html", {
                "message": "Email is invalid"
            })

        if len(password) < 8:
            return render(request, "inkwell/register.html", {
                "message": "Password must be at least 8 characters long"
            })
        elif password != confirmedPassword:
            return render(request, "inkwell/register.html", {
                "message": "Passwords must match"
            })

        if username == "" or email == "" or password == "" or confirmedPassword == "":
            return render(request, "inkwell/register.html", {
                "message": "All fields must be filled in order to register"
            })
        
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            time.sleep(1)
            well = Well(wellOwner=user)
            well.save()
            login(request, user)
            return HttpResponseRedirect(reverse("edit_profile"))
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })

    return render(request, 'inkwell/register.html')
