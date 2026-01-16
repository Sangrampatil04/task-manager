from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
     path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path("edit/<int:task_id>/", views.edit_task, name="edit_task"),
    path("test-reminder/", views.test_reminder),


]
