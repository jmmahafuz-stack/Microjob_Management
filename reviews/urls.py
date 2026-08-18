from django.urls import path

from . import views

urlpatterns = [
    path('create/<int:booking_id>/', views.create_review, name='create_review'),
    path('job/<int:job_id>/create/', views.create_job_review, name='create_job_review'),
    path('history/', views.review_history, name='review_history'),
]
