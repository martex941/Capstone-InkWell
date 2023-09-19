# inkwell/views.py
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.db.models import Sum
from django.urls import reverse
from django.db import IntegrityError

from .helpers import email_validator
from .models import User, Ink

def index(request):
    return render(request, 'inkwell/index.html')

def index_cols(request):
    users = User.objects.all()
    popularAuthors = sorted(users, key=lambda user: user.readers * user.followers, reverse=True)[:10]
    topAuthors = sorted(users, key=lambda user: user.letters * user.coAuthorRequests, reverse=True)[:10]
    topCoAuthors = sorted(users, key=lambda user: user.acceptedRequests, reverse=True)[:10]

    popularAuthors_col = [
        {
            'id': author.id,
            'username': author.username,
            'followers': author.followers
        }
        for author in popularAuthors
    ]
    topAuthors_col = [
        {
            'id': author.id,
            'username': author.username,
            'followers': author.followers
        }
        for author in topAuthors
    ]
    topCoAuthors_col = [
        {
            'id': author.id,
            'username': author.username,
            'followers': author.followers
        }
        for author in topCoAuthors
    ]

    index_columns = {
        'popularAuthors_col': popularAuthors_col,
        'topAuthors_col': topAuthors_col,
        'topCoAuthors_col': topCoAuthors_col

    }

    return JsonResponse(index_columns, safe=False)
    

@login_required
def newInk(request):
    return render(request, "inkwell/newInk.html")

def ink_view(request):
    return render(request, "inkwell/ink_view.html")

@login_required
def well(request, username):
    wellOwner = User.objects.get(username=username)
    inks = Ink.objects.filter(inkOwner=wellOwner.pk)
    co_authors = Ink.objects.filter(inkOwner=wellOwner.pk).values_list('coAuthor', flat=True)
    return render(request, "inkwell/well.html", {
        "wellOwner": wellOwner,
        "inks": inks,
        "ink_number": len(inks),
        "coAuthors": len(co_authors)
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
            return render(request, "inkwell/login.html")
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })

    return render(request, 'inkwell/register.html')
