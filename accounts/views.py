from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import (
    CustomPasswordChangeForm,
    LoginForm,
    ProfileUpdateForm,
    RegisterForm,
)
from .models import CustomUser


def _redirect_for_role(request):
    """Return the canonical landing page for the authenticated user's role."""
    role_urls = {
        "admin": "dashboard_home",
        "worker": "worker_dashboard",
        "customer": "home",
    }
    return redirect(role_urls.get(request.user.role, "home"))


def register_view(request):
    """Create a customer or worker account and send the user to login."""
    if request.user.is_authenticated:
        return _redirect_for_role(request)

    form = RegisterForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        role_label = user.get_role_display()
        messages.success(
            request,
            f"{role_label} account created successfully. Please log in.",
        )
        return redirect("login")

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """
    Authenticate one browser/device session.

    Django stores the authenticated user in the current browser's session.
    A login from another phone/PC therefore does not replace this session.
    """
    if request.user.is_authenticated:
        return _redirect_for_role(request)

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()

        # Reject blocked accounts before creating an authenticated session.
        if getattr(user, "is_blocked", False):
            messages.error(request, "Your account is blocked. Please contact support.")
            return render(request, "accounts/login.html", {"form": form})

        # Workers must be approved before they can enter the worker area.
        if user.role == "worker" and user.worker_status != "APPROVED":
            messages.warning(
                request,
                "Your worker account is waiting for admin approval.",
            )
            return render(request, "accounts/login.html", {"form": form})

        # Keep role/staff flags consistent with the CustomUser model.
        if user.role == "admin":
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["is_staff", "is_superuser"])
        elif user.is_staff or user.is_superuser:
            user.is_staff = False
            user.is_superuser = False
            user.save(update_fields=["is_staff", "is_superuser"])

        # Django rotates the current session key when logging in.
        # This affects only the browser/device making this request.
        login(request, user)
        messages.success(request, f"Welcome {user.first_name or user.username}!")
        return _redirect_for_role(request)

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    """Log out only the current browser/device session."""
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


@login_required
def profile_view(request):
    if request.user.role == "worker":
        from workers.models import WorkerProfile

        WorkerProfile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html")


@login_required
def edit_profile(request):
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "accounts/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = CustomPasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password changed successfully.")
        return redirect("profile")

    return render(
        request,
        "accounts/change_password.html",
        {"form": form},
    )
