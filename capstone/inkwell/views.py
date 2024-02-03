# inkwell/views.py
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse
from django.db import IntegrityError, transaction, models
from django.db.models.functions import Random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time, json

from .helpers import email_validator
from .forms import ChapterForm, CoAuthorRequestForm
from .models import User, Ink, Notification, Well, Follow, Chapter, Post, Comment, CoAuthorRequest, DiscoverAuthors, Tag

def updateDiscoverAuthors(request):
    users = User.objects.all()
    popularAuthors = sorted(users, key=lambda user: (user.readers + user.followers) + (user.readers * user.followers), reverse=True)[:5]
    topAuthors = sorted(users, key=lambda user: (user.letters + user.acceptedCoAuthorRequests) + (user.letters * user.acceptedCoAuthorRequests), reverse=True)[:5]
    topCoAuthors = sorted(users, key=lambda user: user.acceptedCoAuthorRequests, reverse=True)[:5]
    discoverAuthors = User.objects.annotate(random_order=Random()).order_by('random_order')[:10]
    
    try:
        getDiscoverModel = DiscoverAuthors.objects.get(id=1)
        getDiscoverModel.popularAuthors.clear()
        getDiscoverModel.topAuthors.clear()
        getDiscoverModel.topCoAuthors.clear()
        getDiscoverModel.discoverAuthors.clear()
        for user in popularAuthors:
            getDiscoverModel.popularAuthors.add(user)

        for user in topAuthors:
            getDiscoverModel.topAuthors.add(user)

        for user in topCoAuthors:
            getDiscoverModel.topCoAuthors.add(user)

        for user in discoverAuthors:
            getDiscoverModel.discoverAuthors.add(user)

        getDiscoverModel.save()
        print("discover authors updated")
    except DiscoverAuthors.DoesNotExist:
        print("Updating DiscoverAuthors has encountered a problem.")

def mainSearchResults(request, searchQuery):
    if searchQuery == "":
        return redirect('index')
    else:
        authors = User.objects.filter(username__contains=searchQuery)
        inks = Ink.objects.filter(title__contains=searchQuery, privateStatus=False).order_by('-views')
        combined = list(authors) + list(inks)
        pag = Paginator(combined, 10)
        page = request.GET.get('page')
        try:
            pag_items = pag.page(page)
        except PageNotAnInteger:
            pag_items = pag.page(1)
        except EmptyPage:
            pag_items = pag.page(pag.num_pages)

        pages = range(1, pag.num_pages+1)

        return render(request, "inkwell/mainSearchResults.html", {
            "searchQuery": searchQuery,
            "results": pag_items,
            "pages": pages
        })

def mainSearch(request):
    if request.method == "POST":
        query = request.POST.get("mainSearchQuery")
        if query == "":
            return redirect('index')
        return redirect('mainSearchResults', searchQuery=query)

startDate = datetime(2024, 1, 1)

def index(request):
    global startDate
    currentDate = datetime.now()
    timeDifference = currentDate - startDate

    if timeDifference >= timedelta(days=7):
        updateDiscoverAuthors(request)
        
        startDate = currentDate

    disco  = DiscoverAuthors.objects.get(id=1)

    pops = disco.popularAuthors.all()
    popularAuthors = sorted(pops, key=lambda user: (user.readers + user.followers) + (user.readers * user.followers), reverse=True)[:5]

    tops = disco.topAuthors.all()
    topAuthors = sorted(tops, key=lambda user: (user.letters + user.acceptedCoAuthorRequests) + (user.letters * user.acceptedCoAuthorRequests), reverse=True)[:5]
    
    topCos = disco.topCoAuthors.all()
    topCoAuthors = sorted(topCos, key=lambda user: user.yourAcceptedCoAuthorRequests, reverse=True)[:5]

    discoverAuthors = disco.discoverAuthors.all().annotate(random_order=Random()).order_by('random_order')[:10]

    return render(request, 'inkwell/index.html', {
        'popularAuthors': popularAuthors,
        'topAuthors': topAuthors,
        'topCoAuthors': topCoAuthors,
        'discoverAuthors': discoverAuthors,
        'title': "InkWell"
    })

def timeline(request, page):

    def serializeInks(posts, page):
        serialized_inks = [
            {
                'postMessage': post.message,
                'id': post.referencedPostInk.id,
                'title': post.referencedPostInk.title,
                'description': post.referencedPostInk.description,
                'tags': [tag.tagName for tag in post.referencedPostInk.tags.all()],
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
    allPostsPag = Paginator(allPosts, 25)
    try:
        allPosts_col = serializeInks(allPostsPag, page)
    except PageNotAnInteger:
        allPosts_col = serializeInks(allPostsPag, 1)
    except EmptyPage:
        allPosts_col = "EmptyPage"

    followedPosts_col = []
    if request.user.is_authenticated:
        followers = User.objects.filter(followee__follower=request.user)
        followedInks = Ink.objects.filter(inkOwner__in=followers, privateStatus=False)
        followedPosts = Post.objects.filter(referencedPostInk__in=followedInks).order_by('-postCreationDate')
        followedPostsPag = Paginator(followedPosts, 25)
        try:
            followedPosts_col = serializeInks(followedPostsPag, page)
        except PageNotAnInteger:
            followedPosts_col = serializeInks(followedPostsPag, 1)
        except EmptyPage:
            followedPosts_col = "EmptyPage"

    index_columns = {
        'allInks': allPosts_col,
        'followedInks': followedPosts_col,
    }

    return JsonResponse(index_columns, safe=False)

def notifications(request, page):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(notifiedUser=request.user).order_by('-date')
        notificationsPag = Paginator(notifications, 15)
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
    tags = Tag.objects.all()
    if request.method == "POST":
        title = request.POST.get("title")
        newTags = request.POST.get("tagsData").split(',')
        newTags = [BeautifulSoup(tag, 'html.parser').get_text(strip=True) for tag in newTags]
        if newTags:
            readyNewTags = Tag.objects.filter(tagName__in=newTags)
        privateStatus = request.POST.get("privateStatus")
        if privateStatus == "on":
            privateStatus = True
        else:
            privateStatus = False

        description = request.POST.get("description")

        if title == "" or description == "":
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
            description=description, 
            title=title,
            )
        new_ink.save()
        new_ink.tags.add(*readyNewTags)
        new_ink.save()

        time.sleep(1) # 1 second pause for the server to catch up with the newly created ink

        if privateStatus != True:
            new_post = Post(message=f'{current_user.username} created a new Ink "{title}"', referencedPostInk=new_ink)
            new_post.save()

        time.sleep(1) # The page loads quicker than the server so it is held by 1 second for the server to catch up
        return redirect('edit_ink', inkID=new_ink.id)

    return render(request, "inkwell/newInk.html", {
        "title": "New Ink",
        "tags": tags
    })

@login_required
def checkNewInkTitle(request, inkID): # requiring argument inkID is for pages that require it, otherwise it should be written as 0 Example: "0/checkNewInkTitle"
    data = json.loads(request.body)
    title = data.get("check", "")
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

@login_required
def checkNewUsername(request):
    data = json.loads(request.body)
    username = data.get("check", "")
    try:
        userExists = User.objects.get(username=username)
        if userExists:
            messageData = {
                'message': "Username is taken.",
                'color': "red"
            }
            return JsonResponse(messageData, safe=False)
    except User.DoesNotExist:
        messageData = {
            'message': "Username is available.",
            'color': "green"
            }
        return JsonResponse(messageData, safe=False)


def ink_view(request, inkID):
    viewedInk = Ink.objects.get(id=inkID)
    chapters = Chapter.objects.filter(chapterInkOrigin=viewedInk).order_by("chapterNumber")

    # Every time an Ink view is opened, update the view count
    viewedInk.views += 1
    viewedInk.save()

    viewingAsAuthor = False
    following_check = False
    if request.user.is_authenticated:
        current_user = User.objects.get(pk=request.user.pk)

        if current_user == viewedInk.inkOwner:
            viewingAsAuthor = True
        
        try:
            if viewedInk.ink_following.filter(pk=current_user.pk):
                following_check = True
        except Ink.MultipleObjectsReturned:
            pass

    comments = Comment.objects.filter(commentInkOrigin=viewedInk).order_by("-commentCreationDate")

    if request.method == "POST" and "commentContents" in request.POST:
        commentContents = request.POST.get("commentContents")
        new_comment = Comment(content=commentContents, commentInkOrigin=viewedInk, commentAuthor=current_user)
        new_comment.save()
        time.sleep(1)
        return redirect('ink_view', inkID=viewedInk.id)

    return render(request, "inkwell/ink_view.html", {
        "ink": viewedInk,
        "chapters": chapters,
        "following_check": following_check,
        "viewingAsAuthor": viewingAsAuthor,
        "comments": comments
    })

@login_required
def deleteComment(request, commentID):
    if request.method == "POST":
        comment = Comment.objects.get(id=commentID)
        ink = Ink.objects.get(id=comment.commentInkOrigin.id)
        authorsComments = Comment.objects.filter(commentAuthor=request.user).all()
        if comment in authorsComments:
            comment.delete()
            time.sleep(1)
            return redirect('ink_view', inkID=ink.id)

def inkCoAuthors(request, inkID, searchQuery):
    if searchQuery == "":
        coauthors = Ink.objects.get(id=inkID).coAuthors.all()    
    else:
        coauthors = Ink.objects.get(id=inkID).coAuthors.filter(username__contains=searchQuery)

    return render(request, "inkwell/inkCoAuthors.html", {
        "coauthors": coauthors,
        "inkID": inkID
    })

def searchInkCoAuthors(request, inkID):
    if request.method == "POST":
        query = request.POST.get("searchInkCoAuthorsQuery")
        return redirect('inkCoAuthors', inkID=inkID, searchQuery=query)
    else:
        return redirect('inkCoAuthors', inkID=inkID)

@login_required
def followInk(request, inkID):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    viewedInk = Ink.objects.get(id=inkID)
    current_user = User.objects.get(pk=request.user.pk)
    viewedInk.ink_following.add(current_user)
    viewedInk.save()
    new_notification = Notification(
        notifiedUser=viewedInk.inkOwner, 
        contents=f'{current_user.username} just followed your Ink "{viewedInk.title}"', 
        url=f"ink_view/{viewedInk.id}")
    new_notification.save()

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
    tags = Tag.objects.all()
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
        newTags = request.POST.get("tagsData").split(',')
        newTags = [BeautifulSoup(tag, 'html.parser').get_text(strip=True) for tag in newTags]
        newDescription = request.POST.get("descriptionEdit")

        if editInk.updateStatus == False:
            editInk.updateStatus == True

        editInk.title = newInkTitle
        editInk.tags.clear()
        if newTags:
            readyNewTags = Tag.objects.filter(tagName__in=newTags)
            editInk.tags.add(*readyNewTags)
        editInk.description = newDescription
        editInk.save()
        time.sleep(1)

    return render(request, "inkwell/edit_ink.html", {
        "editInk": editInk,
        "tags": tags,
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
                    contents=f'New co-author request from {current_user} regarding Chapter {chapterInfo.chapterNumber}: {chapterInfo.chapterTitle} of ink titled "{inkInfo.title}"', 
                    url=f"coAuthorRequest/{chapterInfo.id}/{new_coAuthorRequest.id}")
                new_notification.save()

                return HttpResponseRedirect(reverse("coAuthorRequest", kwargs={'chapterID': chapterInfo.id, 'requestID': new_coAuthorRequest.id}))
            else:
                print(form.errors)
        else:
            if "deleteChapter" in request.POST:
                subsequentChapters = Chapter.objects.filter(chapterNumber__gt=chapterInfo.chapterNumber)
                with transaction.atomic():
                    chapterInfo.delete()
                    for chapter in subsequentChapters:
                        chapter.chapterNumber -= 1
                        chapter.save()
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
                if inkInfo.privateStatus != True:
                    new_post = Post(message=f'{current_user} updated their ink "{inkInfo.title}"', referencedPostInk=inkInfo)
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
def coAuthorRequestsList(request, searchQuery):
    current_user = User.objects.get(pk=request.user.pk)
    inks = Ink.objects.filter(inkOwner=current_user.id)
    chapters = Chapter.objects.filter(chapterInkOrigin__in=inks)
    if searchQuery == "":
        requests = CoAuthorRequest.objects.filter(requestedChapter__in=chapters).order_by("-requestDate")
    else:
        requests = CoAuthorRequest.objects.filter(Q(requestedChapter__in=chapters) & Q(coAuthor__username__contains=searchQuery) | Q(requestedChapter__chapterInkOrigin__title__contains=searchQuery)).order_by("-requestDate")

    return render(request, "inkwell/coAuthorRequestsList.html", {
        "requests": requests,
        "title": "Co-author requests"
    })

@login_required
def searchCoAuthorRequestsList(request):
    if request.method == "POST":
        query = request.POST.get("searchYourRequestsListQuery")
        return redirect('coAuthorRequestsList', searchQuery=query)
    else:
        return redirect('coAuthorRequestsList')

@login_required
def yourCoAuthorRequests(request, searchQuery):
    current_user = User.objects.get(pk=request.user.pk)
    if searchQuery == "":
        yourRequests = CoAuthorRequest.objects.filter(coAuthor=current_user).order_by("-requestDate")
    else:
        yourRequests = CoAuthorRequest.objects.filter(Q(requestedChapter__chapterInkOrigin__inkOwner__username__contains=searchQuery) | Q(requestedChapter__chapterInkOrigin__title__contains=searchQuery)).order_by("-requestDate")

    return render(request, "inkwell/yourCoAuthorRequests.html", {
        "yourRequests": yourRequests,
        "title": "Your co-author requests"
    })

@login_required
def searchYourCoAuthorRequests(request):
    if request.method == "POST":
        query = request.POST.get("searchYourRequestsQuery")
        return redirect('yourCoAuthorRequests', searchQuery=query)
    else:
        return redirect('yourCoAuthorRequests')

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

            if relatedInk.privateStatus != True:
                new_post = Post(message=f'{relatedRequest.coAuthor.username} updated {relatedInk.inkOwner.username}\'s ink: "{relatedInk.title}"', referencedPostInk=relatedInk)
                new_post.save()

            new_notification = Notification(
                notifiedUser=relatedRequest.coAuthor, 
                contents=f'Your Co-Author request to "{relatedInk.title}" has been accepted.', 
                url=f"coAuthorRequest/{chapterID}/{requestID}")
            new_notification.save()
            time.sleep(1)
            
            return HttpResponseRedirect(reverse("edit_ink", kwargs={'inkID': relatedInk.id}))
        elif "requestDeclined" in request.POST:
            declineReason = request.POST.get("declineReason")
            if declineReason == "":
                return render(request, "inkwell/coAuthorRequest.html", {
                    "originalChapter": originalChapter,
                    "newChapterContent": relatedRequest,
                    "title": "Request review",
                    "message": "Please provide a reason for request denial."
                })
            relatedRequest.declinedMessage = declineReason
            relatedRequest.save()

            new_notification = Notification(
                notifiedUser=relatedRequest.coAuthor, 
                contents=f'Your Co-Author request to "{relatedInk.title}" has been declined.', 
                url=f"ink_view/{relatedInk.id}")
            new_notification.save()
            time.sleep(1)
            
            return HttpResponseRedirect(reverse("coAuthorRequestsList"))

    return render(request, "inkwell/coAuthorRequest.html", {
        "originalChapter": originalChapter,
        "newChapterContent": relatedRequest,
        "title": "Request review"
    })

def well(request, username):
    followCheck = False
    wellOwner = User.objects.get(username=username)
    if request.user.is_authenticated:
        current_user = User.objects.get(pk=request.user.pk)
        if Follow.objects.filter(follower=current_user, followee=wellOwner):
            followCheck = True

    inks = Ink.objects.filter(inkOwner=wellOwner.pk, privateStatus=False)
    followers = wellOwner.followers
    co_authors = wellOwner.acceptedCoAuthorRequests
    
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
            url=f"well/{current_user}")
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

def followers(request, username, searchQuery):
    user = User.objects.get(username=username)
    if searchQuery == "":
        followers = User.objects.filter(follower__followee=user.pk).distinct()
    else:
        followers = User.objects.filter(follower__followee=user.pk, username__contains=searchQuery).distinct()

    pag = Paginator(followers, 20)
    page = request.GET.get('page')
    try:
        pag_items = pag.page(page)
    except PageNotAnInteger:
        pag_items = pag.page(1)
    except EmptyPage:
        pag_items = pag.page(pag.num_pages)

    pages = range(1, pag.num_pages+1)

    return render(request, "inkwell/followers.html", {
        "followers": pag_items,
        "pages": pages,
        "followed_user": user
    })

def searchFollowers(request, username):
    if request.method == "POST":
        query = request.POST.get("searchFollowersQuery")
        return redirect('followers', username=username, searchQuery=query)
    else:
        return redirect('followers', username=username)


def coauthors(request, username, searchQuery):
    user = User.objects.get(username=username)
    userInks = Ink.objects.filter(inkOwner=user.pk)
    if searchQuery == "":
        coauthors = User.objects.filter(CoAuthors__in=userInks).distinct()
    else:
        coauthors = User.objects.filter(CoAuthors__in=userInks, username__contains=searchQuery).distinct()
    
    pag = Paginator(coauthors, 20)
    page = request.GET.get('page')
    try:
        pag_items = pag.page(page)
    except PageNotAnInteger:
        pag_items = pag.page(1)
    except EmptyPage:
        pag_items = pag.page(pag.num_pages)

    pages = range(1, pag.num_pages+1)

    return render(request, "inkwell/coauthors.html", {
        "coauthors": pag_items,
        "pages": pages,
        "user": user
    })

def searchCoAuthors(request, username):
    if request.method == "POST":
        query = request.POST.get("searchCoAuthorsQuery")
        return redirect('coauthors', username=username, searchQuery=query)
    else:
        return redirect('coauthors', username=username)

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
                return render(request, "inkwell/password_change.html", {
                    "message": "Incorrect old password."
                })
            
            # Check if the new password is valid
            if len(new_password) < 8:
                return render(request, "inkwell/password_change.html", {
                    "message": "New password must be at least 8 characters long."
                })
            
            # Check if the new passwords match
            if new_password != new_password_confirm:
                return render(request, "inkwell/password_change.html", {
                    "message": "Passwords must match."
                })

            # Update the user's password
            user.set_password(new_password)
            user.save()
            
            # Update the session to reflect the password change
            update_session_auth_hash(request, user)
            
            return render(request, "inkwell/password_change.html", {
                "message": "Password changed successfully."
            })
        
    return render(request, "inkwell/password_change.html")

@login_required
def username_change(request):
    if request.method == "POST":
        old_username = request.user.username
        new_username = request.POST.get("new_username")
        user = request.user
        if new_username.strip().lower() == old_username.strip().lower():
            return render(request, "inkwell/username_change.html", {
                "message": "New username must be different than the old username."
            })
        elif len(new_username) < 5:
            return render(request, "inkwell/username_change.html", {
                "message": "New username must be at least 5 characters long."
            })
        elif User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            return render(request, "inkwell/username_change.html", {
                "message": "Username is already taken."
            })
        else:
            current_user = User.objects.get(pk=user.pk)
            current_user.username = new_username
            current_user.save()
            time.sleep(1)
            return redirect('username_change')
        
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
def ink_settings(request, inkQuery):
    if inkQuery == "":
        retrieve_inks = Ink.objects.filter(inkOwner=request.user)
    else:
        retrieve_inks = Ink.objects.filter(inkOwner=request.user, title__contains=inkQuery)
    return render(request, "inkwell/ink_settings.html", {
        "inks": retrieve_inks,
        "title": "Ink Settings"
    })

@login_required
def searchInkSettings(request):
    if request.method == "POST":
        query = request.POST.get("searchInkSettingsQuery")
        return redirect('ink_settings', inkQuery=query)
    else:
        return redirect('ink_settings')

@login_required
def privatizeInk(request, inkid, command):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    ink = Ink.objects.get(id=inkid)

    if command == "makePublic":
        ink.privateStatus = False
        ink.save()
        return JsonResponse({"message": "Ink has been made public."}, safe=False)
    elif command == "makePrivate":
        ink.privateStatus = True
        ink.save()
        return JsonResponse({"message": "Ink has been made private."}, safe=False)
    else:
        return JsonResponse({"message": "Wrong command."}, safe=False)

@login_required
def delete_ink(request, inkID):
    selectedInk = Ink.objects.get(id=inkID)
    if request.method == "POST":
        deleteConfirmation = request.POST.get("deleteInkConfirmation")
        if deleteConfirmation == selectedInk.title:
            selectedInk.delete()
            time.sleep(1)
            return HttpResponseRedirect(reverse("ink_settings"))
        else:
            return render(request, "inkwell/delete_ink.html", {
                "selectedInk": selectedInk,
                "inkID": inkID,
                "message": "Invalid title."
            })


    return render(request, "inkwell/delete_ink.html", {
        "selectedInk": selectedInk,
        "inkID": inkID
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
