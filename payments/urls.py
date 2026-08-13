from django.urls import path

from . import views

urlpatterns = [
    # Customer payment flow
    path('checkout/job/<int:job_id>/', views.make_payment, name='make_payment'),
    path('history/', views.payment_history, name='payment_history'),
    
    # Worker payout/earnings flow
    path('earnings/', views.payout_request_list, name='payout_request_list'),
    path('earnings/request/', views.create_payout_request, name='create_payout_request'),
]
