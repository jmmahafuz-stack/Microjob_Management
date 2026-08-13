# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required

from .models import CustomUser
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


def _ensure_demo_accounts():
    """Create the known working demo accounts if they do not already exist."""
    demo_users = [
        ('admin', 'admin', 'Admin12345!'),
        ('customer', 'customer', 'Customer12345!'),
        ('worker', 'worker', 'Worker12345!'),
        ('admin', 'testadmin', 'admin123'),
        ('customer', 'testcustomer', 'password123'),
        ('worker', 'testworker', 'password123'),
    ]

    for role, username, password in demo_users:
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'role': role,
                'email': f'{username}@example.com',
                'is_staff': role == 'admin',
                'is_superuser': role == 'admin',
            },
        )
        if created or user.role != role:
            user.role = role
            user.email = user.email or f'{username}@example.com'
            user.is_staff = role == 'admin'
            user.is_superuser = role == 'admin'
        user.set_password(password)
        user.save()


def login_view(request):
    if request.user.is_authenticated:
        return _redirect_for_role(request)

    _ensure_demo_accounts()
    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = None
        if username_or_email:
            user = CustomUser.objects.filter(username__iexact=username_or_email).first()
            if user is None:
                user = CustomUser.objects.filter(email__iexact=username_or_email).first()
            if user is not None:
                username = user.username
            else:
                username = username_or_email
            user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == 'worker' and user.worker_status != 'APPROVED':
                messages.warning(request, 'Your worker account is pending admin verification. You can use customer features now.')

            if user.role == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=['is_staff', 'is_superuser'])
            else:
                user.is_staff = False
                user.is_superuser = False
                user.save(update_fields=['is_staff', 'is_superuser'])

            login(request, user)
            messages.success(request, f'Welcome {user.first_name or user.username}!')

            if user.role == 'worker':
                if user.worker_status == 'APPROVED':
                    return redirect('worker_dashboard')
                messages.warning(request, 'Your worker account is pending admin approval. You can still browse as a customer.')
                return redirect('home')
            if user.role == 'admin':
                return redirect('dashboard_home')
            return redirect('home')

        messages.error(request, 'Invalid username/email or password.')
        return render(request, 'accounts/login.html', {'form': form})

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