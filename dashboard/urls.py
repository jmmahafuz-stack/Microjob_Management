from django.urls import path

from . import views, admin_views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    
    # Admin Dashboard Routes
    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.admin_users_list, name='admin_users_list'),
    path('admin/users/<int:user_id>/action/', admin_views.admin_user_action, name='admin_user_action'),
    path('admin/payments/', admin_views.admin_payments_list, name='admin_payments_list'),
    path('admin/jobs/', admin_views.admin_jobs_list, name='admin_jobs_list'),
    path('admin/workers/earnings/', admin_views.admin_workers_earnings, name='admin_workers_earnings'),
    path('admin/payouts/', admin_views.admin_payouts_list, name='admin_payouts_list'),
    path('admin/reports/', admin_views.admin_reports, name='admin_reports'),
    path('admin/reports/<str:report_type>/download/', admin_views.admin_report_download, name='admin_report_download'),
    path('admin/api/stats/', admin_views.admin_api_stats, name='admin_api_stats'),
]
