from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('reports/earnings/', views.worker_earnings_report, name='worker_earnings_report'),
    path('profile/<int:pk>/', views.worker_profile_detail, name='worker_profile_detail'),
    path('verify/', views.worker_verification_list, name='worker_verification_list'),
    path('verify/<int:pk>/', views.verify_worker, name='verify_worker'),
]
