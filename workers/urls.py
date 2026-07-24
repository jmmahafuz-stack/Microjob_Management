from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('verify/', views.worker_verification_list, name='worker_verification_list'),
    path('verify/<int:pk>/', views.verify_worker, name='verify_worker'),
]
