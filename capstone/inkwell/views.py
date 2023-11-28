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
from .forms import ChapterForm, CoAuthorRequestForm
from .models import User, Ink, Notification, Well, Follow, Chapter, Post, Comment, CoAuthorRequest

def index(request):
    users = User.objects.all()
    popularAuthors = sorted(users, key=lambda user: user.readers * user.followers, reverse=True)[:10]
    topAuthors = sorted(users, key=lambda user: user.letters * user.acceptedCoAuthorRequests, reverse=True)[:10]
    topCoAuthors = sorted(users, key=lambda user: user.acceptedCoAuthorRequests, reverse=True)[:10]
    discoverAuthors = User.objects.annotate(random_order=Random()).order_by('random_order')[:20]

    return render(request, 'inkwell/index.html', {
        'popularAuthors': popularAuthors,
        'topAuthors': topAuthors,
        'topCoAuthors': topCoAuthors,
        'discoverAuthors': discoverAuthors,
        'title': "InkWell"
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

        if title == "" or genre == "" or description == "":
            return render(request, "inkwell/newInk.html", {
                "messages": ["All fields must be filled."]
            })

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

        if privateStatus != False:
            new_post = Post(message=f"{current_user.username} created a new Ink titled {title}", referencedPostInk=new_ink)
            new_post.save()

        time.sleep(1) # The page loads quicker than the server so it is held by 1 second for the server to catch up
        return HttpResponseRedirect(reverse("edit_ink") + f'?inkID={new_ink.id}')

    return render(request, "inkwell/newInk.html", {
        "title": "New Ink"
    })

@login_required
def checkNewInkTitle(request, inkID): # requiring argument inkID is for pages that require it, otherwise it should be written as 0 Example: "0/checkNewInkTitle"
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
    chapters = Chapter.objects.filter(chapterInkOrigin=viewedInk).order_by("chapterNumber")
    current_user = User.objects.get(pk=request.user.pk)
    following_check = False

    viewingAsAuthor = False
    if current_user == viewedInk.inkOwner:
        viewingAsAuthor = True

    # Every time an Ink view is opened, update the view count
    viewedInk.views += 1
    viewedInk.save()

    try:
        ink_followed = Ink.objects.get(ink_following=current_user)
        if ink_followed:
            following_check = True
    except Ink.DoesNotExist:
        pass

    comments = Comment.objects.filter(commentInkOrigin=viewedInk).order_by("-commentCreationDate")

    if request.method == "POST":
        if "commentContents" in request.POST:
            commentContents = request.POST.get("commentContents")
            new_comment = Comment(content=commentContents, commentInkOrigin=viewedInk, commentAuthor=current_user)
            new_comment.save()
            time.sleep(1)

    return render(request, "inkwell/ink_view.html", {
        "ink": viewedInk,
        "chapters": chapters,
        "following_check": following_check,
        "viewingAsAuthor": viewingAsAuthor,
        "comments": comments
    })

@login_required
def followInk(request, inkID):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    viewedInk = Ink.objects.get(id=inkID)
    current_user = User.objects.get(pk=request.user.pk)
    viewedInk.ink_following.add(current_user)
    viewedInk.save()

    return JsonResponse({"message": "Ink followed"}, status=201)
        

@login_required
def unfollowInk(request, inkID):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    viewedInk = Ink.objects.get(id=inkID)
    current_user = User.objects.get(pk=request.user.pk)
    viewedInk.ink_following.remove(current_user)
    viewedInk.save()

    return JsonResponse({"message": "Ink unfollowed"}, status=201)


@login_required
def edit_ink(request, inkID):
    editInk = Ink.objects.get(id=inkID)
    chapters = Chapter.objects.filter(chapterInkOrigin=editInk.id).order_by("chapterNumber")
    if chapters:
        lastChapter = chapters.last().chapterNumber
    else:
        lastChapter = 0

    current_user = User.objects.get(pk=request.user.pk)
    editingAsCoAuthor = False
    if current_user != editInk.inkOwner:
        editingAsCoAuthor = True

    if request.method == "POST":
        newInkTitle = request.POST.get("title")
        newGenre = request.POST.get("genresEdit")
        newDescription = request.POST.get("descriptionEdit")

        if editInk.updateStatus == False:
            editInk.updateStatus == True

        editInk.title = newInkTitle
        editInk.genre = newGenre
        editInk.description = newDescription
        editInk.save()
        time.sleep(1)

    return render(request, "inkwell/edit_ink.html", {
        "editInk": editInk,
        "chapters": chapters,
        "newChapterNum": (lastChapter + 1),
        "editingAsCoAuthor": editingAsCoAuthor,
        "title": "Editing Ink"
    })

@login_required
def addNewChapter(request, newChapterNumber, inkId):
    if request.method == "POST":
        newChapterTitle = request.POST.get("newChapterTitle")
        inkOrigin = Ink.objects.get(id=inkId)
        new_chapter = Chapter(chapterNumber=newChapterNumber, chapterTitle=newChapterTitle, chapterInkOrigin=inkOrigin)
        new_chapter.save()
        time.sleep(1) # Necessary for the server to catch up making the new chapter model
        return HttpResponseRedirect(reverse("edit_chapter", kwargs={'chapterID': new_chapter.id, 'inkID': inkOrigin.id}))
    
@login_required
def edit_chapter(request, chapterID, inkID):
    chapterInfo = Chapter.objects.get(id=chapterID)
    inkInfo = Ink.objects.get(id=inkID)
    initial_data = {
        "chapterTitle": chapterInfo.chapterTitle,
        "chapterContents": chapterInfo.chapterContents
    }
    form = ChapterForm(initial=initial_data)
    current_user = User.objects.get(pk=request.user.pk)
    editingAsCoAuthor = False
    if current_user != inkInfo.inkOwner:
        editingAsCoAuthor = True

    if request.method == "POST":
        if editingAsCoAuthor:
            form = CoAuthorRequestForm(request.POST)
            if form.is_valid():
                # Create new co-author request
                new_coAuthorRequest = CoAuthorRequest(coAuthor=current_user, requestedChapter=chapterInfo)
                new_coAuthorRequest.save()
                time.sleep(1)

                # Update the new co-author request using the form
                form = CoAuthorRequestForm(request.POST, instance=new_coAuthorRequest)
                form.save()
                time.sleep(1)

                # Create a notification for the author
                new_notification = Notification(
                    notifiedUser=inkInfo.inkOwner, 
                    contents=f"New co-author request from {current_user} regarding Chapter {chapterInfo.chapterNumber}: {chapterInfo.chapterTitle} of ink titled {inkInfo.title}", 
                    url=f"coAuthorRequest/{chapterInfo.id}/{new_coAuthorRequest.id}")
                new_notification.save()

                # Update requests counter for the user who is the author
                inkAuthor = inkInfo.inkOwner
                inkAuthor.YourCoAuthorRequests += 1
                inkAuthor.save()

                return HttpResponseRedirect(reverse("coAuthorRequest", kwargs={'chapterID': chapterInfo.id, 'requestID': new_coAuthorRequest.id}))
            else:
                print(form.errors)
        else:
            if "deleteChapter" in request.POST:
                    chapterInfo.delete()
                    time.sleep(1)
                    return HttpResponseRedirect(reverse("edit_ink", kwargs={'inkID': inkID}))
            form = ChapterForm(request.POST)
            if form.is_valid():
                form = ChapterForm(request.POST, instance=chapterInfo)
                form.save()
                if inkInfo.updateStatus == False:
                    inkInfo.updateStatus == True
                inkInfo.save()
                time.sleep(1)
                if inkInfo.privateStatus != False:
                    new_post = Post(message="updated their ink", referencedPostInk=inkInfo)
                    new_post.save()
                return HttpResponseRedirect(reverse("edit_ink", kwargs={'inkID': inkID}))
        
    return render(request, "inkwell/edit_chapter.html", {
        "chapterInfo": chapterInfo,
        "inkID": inkID,
        "form": form,
        "editingAsCoAuthor": editingAsCoAuthor,
        "title": "Editing chapter"
    })

@login_required
def coAuthorRequestsList(request):
    current_user = User.objects.get(pk=request.user.pk)
    inks = Ink.objects.filter(inkOwner=current_user.id)
    chapters = Chapter.objects.filter(chapterInkOrigin__in=inks)
    requests = CoAuthorRequest.objects.filter(requestedChapter__in=chapters, acceptedStatus=False)

    return render(request, "inkwell/coAuthorRequestsList.html", {
        "requests": requests,
        "title": "Co-author requests"
    })

@login_required
def yourCoAuthorRequests(request):
    current_user = User.objects.get(pk=request.user.pk)
    yourRequests = CoAuthorRequest.objects.filter(coAuthor=current_user)

    return render(request, "inkwell/yourCoAuthorRequests.html", {
        "yourRequests": yourRequests,
        "title": "Your co-author requests"
    })

@login_required
def coAuthorRequest(request, chapterID, requestID):
    originalChapter = Chapter.objects.get(id=chapterID)
    relatedRequest = CoAuthorRequest.objects.get(id=requestID)
    relatedInk = originalChapter.chapterInkOrigin

    if request.method == "POST":
        if "requestAccepted" in request.POST:
            relatedRequest.acceptedStatus = True
            relatedRequest.save()

            relatedInk.coAuthors.add(relatedRequest.coAuthor)
            relatedInk.save()

            originalChapter.chapterContents = relatedRequest.chapterContents
            originalChapter.save()

            if relatedInk.privateStatus != False:
                new_post = Post(message=f"{relatedRequest.coAuthor.username} updated {relatedInk.inkOwner.username}'s ink: {relatedInk.title}", referencedPostInk=relatedInk)
                new_post.save()

            new_notification = Notification(
                notifiedUser=relatedRequest.coAuthor, 
                contents=f"Your Co-Author request to {relatedInk.title} has been accepted.", 
                url=f"coAuthorRequest/{chapterID}/{requestID}")
            new_notification.save()
            time.sleep(1)
            
            return HttpResponseRedirect(reverse("edit_ink", kwargs={'inkID': relatedInk.id}))
        elif "requestDeclined" in request.POST:
            declineReason = request.POST.get("declineReason")
            relatedRequest.declinedMessage = declineReason
            relatedRequest.save()

            new_notification = Notification(
                notifiedUser=relatedRequest.coAuthor, 
                contents=f"Your Co-Author request to {relatedInk.title} has been declined.", 
                url=f"ink_view/{relatedInk.id}")
            new_notification.save()
            time.sleep(1)
            
            return HttpResponseRedirect(reverse("coAuthorRequestsList"))

    return render(request, "inkwell/coAuthorRequest.html", {
        "originalChapter": originalChapter,
        "newChapterContent": relatedRequest,
        "title": "Request review"
    })

@login_required
def well(request, username):
    current_user = User.objects.get(pk=request.user.pk)
    wellOwner = User.objects.get(username=username)
    inks = Ink.objects.filter(inkOwner=wellOwner.pk)
    followers = wellOwner.followers
    co_authors = wellOwner.acceptedCoAuthorRequests
    followCheck = False
    if Follow.objects.filter(follower=current_user, followee=wellOwner):
        followCheck = True

    return render(request, "inkwell/well.html", {
        "wellOwner": wellOwner,
        "inks": inks,
        "followers": followers,
        "ink_number": len(inks),
        "coAuthors": co_authors,
        "followCheck": followCheck,
        "title": f"{wellOwner}'s InkWell"
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
        # Create a new follow linking the users
        new_follow = Follow(follower=current_user, followee=followed_user)
        new_follow.save()
        time.sleep(1)

        # Create a notification for the followed user
        new_notification = Notification(
            notifiedUser=followed_user, 
            contents=f"{current_user} followed you.", 
            url=f"well/{followed_user.username}/followers")
        new_notification.save()

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
    followers = User.objects.filter(follower__followee=user.pk).distinct()

    return render(request, "inkwell/followers.html", {
        "followers": followers,
        "followed_user": user
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
