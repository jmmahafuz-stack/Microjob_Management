from django.urls import path

from . import views

urlpatterns = [
    path('checkout/<int:pk>/', views.make_payment, name='make_payment'),
    path('history/', views.payment_history, name='payment_history'),
]
