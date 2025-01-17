from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'property'
urlpatterns = [
    path('', views.redirect_to_opportunities, name = 'redirect_to_opportunities'),
    path('<str:development>/overview', views.view_overview, name = 'view_overview'),
    path('<str:development>/properties', views.view_opportunities, name = 'view_opportunities'),
    path('<str:development>/properties/<int:id>', views.view_opportunity, name='view_opportunity'),
]