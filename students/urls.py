from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.add_student, name='add_student'),
    path('<int:id>/', views.student_detail, name='student_detail'),
    path('<int:id>/add-mark/', views.add_mark, name='add_mark'),
    path('<int:id>/delete/', views.delete_student, name='delete_student'),
    path('<int:id>/edit/', views.edit_student, name='edit_student'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
   
]   