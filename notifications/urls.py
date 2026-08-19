from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
    path('<int:pk>/read/', views.mark_as_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_notifications_read'),
    path('api/unread-count/', views.get_unread_count, name='unread_count_api'),
]
