from django.urls import path
from . import views

urlpatterns = [

    path('', views.service_list, name='service_list'),

    path(
        '<int:pk>/',
        views.service_detail,
        name='service_detail'
    ),
    path(
        '<int:pk>/favorite/',
        views.toggle_favorite_service,
        name='toggle_favorite_service'
    ),

    path(
        'create/',
        views.create_service,
        name='create_service'
    ),

    path(
        'edit/<int:pk>/',
        views.edit_service,
        name='edit_service'
    ),

    path(
        'delete/<int:pk>/',
        views.delete_service,
        name='delete_service'
    ),
]