from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.MainView.as_view(), name='home'),
    path('about/',views.AboutView.as_view(), name='about')
]