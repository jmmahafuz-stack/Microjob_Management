from django.urls import path

from . import views

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('history/', views.booking_history, name='booking_history'),
    path('create/', views.create_booking, name='create_booking'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/edit/', views.edit_booking, name='edit_booking'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<int:pk>/assign/', views.assign_worker, name='assign_worker'),
    path('<int:pk>/status/', views.update_status, name='update_status'),
    path('<int:pk>/respond/<str:action>/', views.respond_to_booking, name='respond_to_booking'),
    path('<int:pk>/invoice/', views.invoice, name='invoice'),
    
    # ===== PHASE 2: Service Request Workflow =====
    path('requests/', views.service_request_list, name='service_request_list'),
    path('requests/create/', views.service_request_create, name='service_request_create'),
    path('requests/<int:pk>/', views.service_request_detail, name='service_request_detail'),
    path('requests/<int:service_request_id>/apply/', views.job_application_create, name='job_application_create'),
    path('applications/<int:pk>/review/', views.job_application_review, name='job_application_review'),
    path('worker-jobs/', views.worker_my_jobs, name='worker_my_jobs'),
    path('jobs/', views.worker_available_jobs, name='worker_available_jobs'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/accept/', views.job_accept, name='job_accept'),
    path('jobs/<int:pk>/messages/', views.job_messages, name='job_messages'),
    path('jobs/<int:pk>/complete/', views.job_complete, name='job_complete'),
    path('jobs/<int:pk>/cancel/', views.cancel_job, name='cancel_job'),
]
