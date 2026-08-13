from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue.')
            return redirect('login')
        if request.user.role != 'customer':
            messages.error(request, 'Only customers can access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def worker_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue.')
            return redirect('login')
        if request.user.role != 'worker':
            messages.error(request, 'Only workers can access this page.')
            return redirect('home')
        if request.user.worker_status != 'APPROVED':
            messages.error(request, 'Your worker account is not approved yet.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue.')
            return redirect('login')
        if request.user.role != 'admin':
            messages.error(request, 'Only admins can access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def staff_member_required(view_func):
    """Decorator to check if user is staff/admin"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue.')
            return redirect('login')
        if not request.user.is_staff or request.user.role != 'admin':
            messages.error(request, 'Only staff members can access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
