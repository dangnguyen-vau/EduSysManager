from django.urls import path
from . import views

urlpatterns = [
    # Auth routes
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('staff/register/', views.register_staff, name='register_staff'),
    path('staff/', views.staff_list, name='staff_list'),
    
    # Main routes
    path('', views.home, name='home'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<uuid:transaction_id>/approve/', views.approve_transaction, name='approve_transaction'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('mine/', views.mine_block, name='mine_block'),
    path('verify/', views.verify_chain, name='verify_chain'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.add_course, name='add_course'),
    path('statistics/', views.statistics, name='statistics'),
] 