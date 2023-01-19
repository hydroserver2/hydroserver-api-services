from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, get_user_model

from .forms import SignUpForm


def home_view(request):
    return render(request, 'registration/home.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=request.POST['username']).exists():
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('sites')
            else:
                messages.error(request, 'Username or password is incorrect')
        else:
            messages.error(request, 'Username does not exist')

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect("home")


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
