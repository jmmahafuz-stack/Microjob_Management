from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification


@login_required
def notification_list(request):
    """List all notifications for the logged-in user."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def notification_detail(request, pk):
    """View a single notification."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    # Mark as read
    notification.mark_as_read()
    
    return render(request, 'notifications/notification_detail.html', {
        'notification': notification,
    })


@login_required
def mark_as_read(request, pk):
    """Mark a notification as read (AJAX or redirect)."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_read': True})
    
    return redirect(request.GET.get('next', 'notification_list'))


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read for the user."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')


@login_required
def get_unread_count(request):
    """Get count of unread notifications (AJAX)."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})
