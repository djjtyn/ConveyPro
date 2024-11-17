from django.urls import path
from . import views

app_name = 'property'
urlpatterns = [
    path('', views.view_opportunities, name = 'view_opportunities') ,
    path('<int:id>/', views.view_opportunity, name='view_opportunity'),
]