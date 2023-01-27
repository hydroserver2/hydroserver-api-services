from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignUpForm, UpdateAccountForm
from .models import CustomUser


def home_view(request):
    return render(request, 'registration/home.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('sites')
        else:
            messages.error(request, 'Username or password is incorrect')

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


@login_required(login_url="login")
def profile(request):
    user = request.user
    custom_user = CustomUser.objects.get(username=user)
    organization = custom_user.organization
    return render(request, 'registration/profile.html', {'user': custom_user, 'organization': organization})


@login_required(login_url="login")
def update_account(request):
    if request.method == 'POST':
        form = UpdateAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        form = UpdateAccountForm(instance=request.user)
    return render(request, 'registration/update-account.html', {'form': form})


@login_required(login_url="login")
def remove_account(request):
    if request.method == 'POST':
        user_confirm = request.POST.get('confirm')
        if user_confirm == 'yes' and request.user.is_authenticated:
            request.user.delete()
            logout(request)
            messages.success(request, 'Your account has been removed!')
            return redirect('home')
        else:
            messages.info(request, 'Account removal cancelled.')
            return redirect('profile')
    return render(request, 'registration/remove-account.html')
