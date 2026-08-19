from django.urls import path

from . import views

urlpatterns = [
    path('create/<int:booking_id>/', views.create_complaint, name='create_complaint'),
    path('history/', views.complaint_history, name='complaint_history'),
    path('contact-admin/', views.contact_admin, name='contact_admin'),
    path('reply/<int:pk>/', views.reply_to_complaint, name='reply_to_complaint'),
]
