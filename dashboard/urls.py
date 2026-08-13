from django.urls import path

from . import views, admin_views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    
    # Admin Dashboard URLs
    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.admin_users_list, name='admin_users_list'),
    path('admin/payments/', admin_views.admin_payments_list, name='admin_payments_list'),
    path('admin/jobs/', admin_views.admin_jobs_list, name='admin_jobs_list'),
    path('admin/workers/earnings/', admin_views.admin_workers_earnings, name='admin_workers_earnings'),
    path('admin/payouts/', admin_views.admin_payouts_list, name='admin_payouts_list'),
    path('admin/reports/', admin_views.admin_reports, name='admin_reports'),
    
    # Report Downloads
    path('admin/reports/payment/download/', admin_views.download_payment_report, name='download_payment_report'),
    path('admin/reports/worker/download/', admin_views.download_worker_report, name='download_worker_report'),
    path('admin/reports/job/download/', admin_views.download_job_report, name='download_job_report'),
    path('admin/reports/commission/download/', admin_views.download_commission_report, name='download_commission_report'),
    path('admin/reports/financial/download/', admin_views.download_financial_report, name='download_financial_report'),
    
    # AJAX endpoints
    path('admin/api/stats/', admin_views.get_dashboard_stats_json, name='dashboard_stats_json'),
]
