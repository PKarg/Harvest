from django.urls import path

from . import views

app_name = "harvest"

urlpatterns = [
    path('', views.index, name="home"),
    path('list/', views.harvest_list, name="harvest-list"),
    path('add/', views.harvest_add, name="harvest-add"),
    path('edit/<int:pk>', views.harvest_edit, name="harvest-edit"),
    path('delete/<int:pk>', views.harvest_delete, name="harvest-delete"),
]
