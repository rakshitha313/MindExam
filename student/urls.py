from django.urls import path
from student import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
app_name = 'student'

urlpatterns = [

    path('studentsignup/', views.student_signup_view, name='studentsignup'),

    path('student-dashboard/', views.student_dashboard_view, name='student-dashboard'),
    path('sustainable-travel/', views.sustainable_travel_view, name='sustainable-travel'),
    path('student-exam/', views.student_exam_view, name='student-exam'),
    path('edit-profile/', views.edit_profile_view, name='edit-profile'),

    path('take-exam/<int:pk>/', views.take_exam_view, name='take_exam'),
    path('start-exam/<int:pk>/', views.start_exam_view, name='start_exam'),
    path('verify/<int:pk>/', views.verify_exam_access, name='verify_exam_access'),

    path('change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='student/change_password.html',
            success_url='/student/student-dashboard/'
        ),
        name='change-password'
    ),

    path('password_reset/', auth_views.PasswordResetView.as_view(
    template_name='student/password_reset.html'
), name='password_reset'),

    path('password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='student/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='student/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path('reset_done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='student/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    path('doubts/', views.student_doubts, name='student-doubts'),
    path('calculate-marks/', views.calculate_marks_view, name='calculate-marks'),
    path('bookmark/<int:pk>/', views.bookmark_question, name='bookmark'),
    path('view-result/', views.view_result_view, name='view-result'),
    path('check-marks/<int:pk>/', views.check_marks_view, name='check-marks'),
    path('student-marks/', views.student_marks_view, name='student-marks'),

    path('leaderboard/', views.student_leaderboard_view, name='student-leaderboard'),
    path('course-leaderboard/<int:pk>/', views.course_leaderboard_view, name='course-leaderboard'),
    
    path('certificate/<int:pk>/', views.certificate_view, name='certificate'),
    path('review-exam/<int:pk>/', views.review_exam_view, name='review-exam'),
    path('practice-exam/', views.practice_exam_view, name='practice-exam'),

    path('notifications/', views.notifications_view, name='notifications'),
    path('settings/', views.student_settings_view, name='student-settings'),


]