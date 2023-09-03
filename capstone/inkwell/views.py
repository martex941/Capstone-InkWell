# inkwell/views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import IntegrityError

from helpers import email_validator
from models import User

def index(request):
    return render(request, 'inkwell/index.html')

def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        
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

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":

        # Necessary variables
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmedPassword = request.POST["confirmed_password"]
        users = User.objects.all()

        # Check various conditions 
        if len(username) < 5:
            return render(request, "inkwell/register.html", {
                "message": "Username must be at least 5 characters long"
            })
        
        if email in users.email:
            return render(request, "inkwell/register.html", {
                "message": "Email is already taken"
            })

        if email_validator(email) == False:
            return render(request, "inkwell/register.html", {
                "message": "Email is invalid"
            })

        if len(password) < 8:
            return render(request, "inkwell/register.html", {
                "message": "Password must be at least 8 characters long"
            })

        if password != confirmedPassword:
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
