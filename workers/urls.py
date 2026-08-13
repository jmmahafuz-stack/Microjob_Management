from django.urls import path

from . import views, dashboard_views

urlpatterns = [
    path('dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('reports/earnings/', views.worker_earnings_report, name='worker_earnings_report'),
    path('profile/<int:pk>/', views.worker_profile_detail, name='worker_profile_detail'),
    path('verify/', views.worker_verification_list, name='worker_verification_list'),
    path('verify/<int:pk>/', views.verify_worker, name='verify_worker'),
    
    # Enhanced dashboard routes
    path('earnings-detail/', dashboard_views.worker_earnings_detail, name='worker_earnings_detail'),
    path('transaction-history/', dashboard_views.worker_transaction_history, name='worker_transaction_history'),
    path('payout-requests/', dashboard_views.worker_payout_requests, name='worker_payout_requests'),
    path('profile-edit/', dashboard_views.worker_profile_edit, name='worker_profile_edit'),
    path('payment-methods/', dashboard_views.worker_payment_methods, name='worker_payment_methods'),
]
