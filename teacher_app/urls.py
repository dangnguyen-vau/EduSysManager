from django.urls import path
from . import views

urlpatterns = [
    # Auth routes
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    
    # Main routes
    path('', views.teacher_home, name='teacher_home'),
    path('add-score/', views.add_score, name='add_score'),
    path('score-history/', views.score_history, name='score_history'),
    path('students/', views.teacher_student_list, name='teacher_student_list'),
    path('courses/', views.teacher_course_list, name='teacher_course_list'),
    
    # API endpoints
    path('api/student-scores/<int:student_id>/', views.api_student_scores, name='api_student_scores'),
    path('api/course-scores/<int:course_id>/', views.api_course_scores, name='api_course_scores'),
]
