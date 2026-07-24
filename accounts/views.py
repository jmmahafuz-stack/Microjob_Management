# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from .forms import (
    RegisterForm,
    LoginForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm
)


def _redirect_for_role(request):
    if request.user.role == 'admin':
        return redirect('dashboard_home')
    if request.user.role == 'worker':
        return redirect('worker_dashboard')
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return _redirect_for_role(request)

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            role_label = 'worker' if form.cleaned_data.get('role') == 'worker' else 'customer'
            messages.success(request, f'{role_label.title()} account created successfully. Please login.')
            return redirect('login')

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return _redirect_for_role(request)

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()

            if user.role == 'worker' and not user.is_verified_worker:
                messages.error(request, 'Your worker account is pending verification. Please wait for admin approval.')
                return render(request, 'accounts/login.html', {'form': form})

            if user.role == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=['is_staff', 'is_superuser'])
            else:
                user.is_staff = False
                user.is_superuser = False
                user.save(update_fields=['is_staff', 'is_superuser'])

            login(request, user)
            messages.success(request, f'Welcome {user.first_name}!')
            if user.role == 'worker':
                return redirect('worker_dashboard')
            if user.role == 'admin':
                return redirect('dashboard_home')
            return redirect('home')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


@login_required
def profile_view(request):
    if request.user.role == 'worker':
        from workers.models import WorkerProfile
        WorkerProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')

    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            messages.success(request, 'Password changed successfully.')
            return redirect('profile')

    else:
        form = CustomPasswordChangeForm(request.user)

    return render(
        request,
        'accounts/change_password.html',
        {'form': form}
    )