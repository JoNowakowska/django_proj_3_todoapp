from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate


ERROR_PWD_DONT_MATCH = "Passwords don't match. Please try again."
ERROR_USERNAME_TAKEN = "This username has been already taken. Please sign up with another username."
ERROR_WRONG_CREDENTIALS = "Username and password did not match. Please try again."


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST.get('password1') != request.POST.get('password2'):
            return render(request, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': ERROR_PWD_DONT_MATCH})
        else:
            try:
                user = User.objects.create_user(request.POST.get('username'), password=request.POST.get('password1'))
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': ERROR_USERNAME_TAKEN})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None:
            return render(request, 'todo/loginuser.html',
                          {'form': AuthenticationForm(), 'error': ERROR_WRONG_CREDENTIALS})
        else:
            login(request, user)
            return redirect('currenttodos')


def currenttodos(request):
    return render(request, 'todo/currenttodos.html')


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')