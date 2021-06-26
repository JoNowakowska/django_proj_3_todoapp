from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone

from .forms import TodoForm
from .models import Todo


ERROR_PWD_DONT_MATCH = "Passwords don't match. Please try again."
ERROR_USERNAME_TAKEN = "This username has been already taken. Please sign up with another username."
ERROR_WRONG_CREDENTIALS = "Username and password did not match. Please try again."
ERROR_WRONG_VALUE = "Something went wrong. Please enter correct values into the form."


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


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm})
    elif request.method == 'POST':
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm, 'error': ERROR_WRONG_VALUE})


@login_required
def currenttodos(request):
    current_todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo/currenttodos.html', {'current_todos': current_todos})


@login_required
def viewtodo(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    elif request.method == "POST":
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': ERROR_WRONG_VALUE})


@login_required
def completed_todo(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    if request.method == "POST":
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deleted_todo(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect('currenttodos')


@login_required
def completedtodos(request):
    completed_todos = Todo.objects.filter(user=request.user, date_completed__isnull=False)
    return render(request, 'todo/completedtodos.html', {'completed_todos': completed_todos})


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')