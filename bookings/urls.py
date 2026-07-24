from django.urls import path

from . import views

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('history/', views.booking_history, name='booking_history'),
    path('create/', views.create_booking, name='create_booking'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/edit/', views.edit_booking, name='edit_booking'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<int:pk>/assign/', views.assign_worker, name='assign_worker'),
    path('<int:pk>/status/', views.update_status, name='update_status'),
    path('<int:pk>/respond/<str:action>/', views.respond_to_booking, name='respond_to_booking'),
    path('<int:pk>/invoice/', views.invoice, name='invoice'),
]
