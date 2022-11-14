from django.urls import path

from . import views

app_name = "harvest"

urlpatterns = [
    path('', views.index, name="home"),
]
