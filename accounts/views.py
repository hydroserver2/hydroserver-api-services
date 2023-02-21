from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignUpForm, UpdateAccountForm, OrganizationForm
from .models import CustomUser, Organization, Membership


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
    user = request.user.username
    custom_user = CustomUser.objects.get(username=user)
    organizations = custom_user.organizations.all()
    return render(request, 'registration/profile.html', {'user': custom_user, 'organizations': organizations})


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


@login_required(login_url="login")
def create_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            membership = Membership.objects.create(user=request.user, organization=organization, is_admin=True)
            membership.save()
            return redirect('profile')
    else:
        form = OrganizationForm()
    return render(request, 'registration/create-organization.html', {'form': form})


@login_required(login_url="login")
def update_organization(request, pk):
    organization = Organization.objects.get(pk=pk)
    membership = Membership.objects.get(user=request.user, organization=organization)
    if not membership.is_admin:
        messages.info(request, 'You are not an admin for this organization so editing is restricted.')
        return redirect('profile')
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = OrganizationForm(instance=organization)
    return render(request, 'registration/update-organization.html', {'form': form, 'organization_pk': pk})


@login_required(login_url="login")
def delete_organization(request, pk):
    organization = Organization.objects.get(pk=pk)
    membership = Membership.objects.get(user=request.user, organization=organization)
    if not membership.is_admin:
        messages.info(request, 'You are not an admin for this organization so deleting is restricted.')
        return redirect('profile')
    if request.method == 'POST':
        user_confirm = request.POST.get('confirm')
        if user_confirm == 'Permanently Delete Organization' and request.user.is_authenticated:
            organization.delete()
            messages.success(request, 'Organization has been removed!')
        else:
            messages.info(request, 'Organization removal cancelled.')
        return redirect('profile')
    return render(request, 'registration/delete-organization.html')


@login_required(login_url="login")
def add_organization_admin(request, pk):
    organization = Organization.objects.get(pk=pk)
    membership = Membership.objects.get(user=request.user, organization=organization)
    if not membership.is_admin:
        messages.info(request, 'You are not an admin for this organization so adding an admin is restricted.')
        return redirect('profile')
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.info(request, f'User {username} does not exist.')
            return redirect('profile')
        try:
            org_membership = Membership.objects.get(user=user, organization=organization)
            org_membership.is_admin = True
            org_membership.save()
        except Membership.DoesNotExist:
            Membership.objects.create(user=user, organization=organization, is_admin=True)
        messages.success(request, f'{username} is now an admin for {organization.name}.')
        return redirect('profile')
    return render(request, 'registration/add-organization-admin.html', {'organization_pk': pk})

