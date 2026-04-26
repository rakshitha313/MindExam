from django.contrib import admin
from django.urls import path, include
from exam import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name=''),
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    
    # Redirections for legacy URLs
    path('studentlogin/', views.login_view, name='studentlogin'),
    path('teacherlogin/', views.login_view, name='teacherlogin'),
    path('adminlogin/', views.login_view, name='adminlogin'),
    path('adminsignup/', views.admin_signup_view, name='adminsignup'),

    # Admin Dashboard & Command Hubs
    path('admin-dashboard/', views.admin_dashboard_view, name='admin-dashboard'),
    path('admin-teacher/', views.admin_teacher_view, name='admin-teacher'),
    path('admin-student/', views.admin_student_view, name='admin-student'),
    path('admin-course/', views.admin_course_view, name='admin-course'),
    path('admin-question/', views.admin_question_view, name='admin-question'),

    # Admin List Views
    path('admin-view-teacher/', views.admin_view_teacher_view, name='admin-view-teacher'),
    path('admin-view-student/', views.admin_view_student_view, name='admin-view-student'),
    path('admin-view-course/', views.admin_view_course_view, name='admin-view-course'),
    # List all questions
    # urls.py
path('admin-view-question/<int:exam_id>/', views.admin_view_question_view, name='admin-view-question'),
    
    path('admin-view-pending-exams/', views.admin_view_pending_exams_view, name='admin-view-pending-exams'),
    path('admin-view-pending-teacher/', views.admin_view_pending_teacher_view, name='admin-view-pending-teacher'),
    path('update-student/<int:pk>/', views.update_student_view, name='update-student'),
    path('delete-student/<int:pk>/', views.delete_student_view, name='delete-student'),
    # Admin Reports & Analytics
    path('admin-view-results/', views.admin_view_results_view, name='admin-view-results'),
    path('admin-view-marks/<int:pk>/', views.admin_view_marks_view, name='admin-view-marks'),
    path('admin-view-teacher-salary/', views.admin_view_teacher_salary_view, name='admin-view-teacher-salary'),

    path('admin-check-marks/<int:pk>', views.admin_check_marks_view, name='admin-check-marks'),

    # Admin Creation Forms
    path('admin-add-teacher/', views.admin_add_teacher_view, name='admin-add-teacher'),
    path('admin-add-course/', views.admin_add_course_view, name='admin-add-course'),
    path('admin-add-question/', views.admin_add_question_view, name='admin-add-question'),
    path('admin-conduct-exam/', views.admin_conduct_exam_view, name='admin-conduct-exam'),

    # Admin State Actions
    path('admin-approve-exam/<int:pk>', views.admin_approve_exam_view, name='admin-approve-exam'),
    path('admin-reject-exam/<int:pk>', views.admin_reject_exam_view, name='admin-reject-exam'),
    path('admin-settings/', views.admin_settings_view, name='admin-settings'),
    path('approve-teacher/<int:pk>/', views.admin_approve_teacher_view, name='admin-approve-teacher'),
path('reject-teacher/<int:pk>/', views.admin_reject_teacher_view, name='admin-reject-teacher'),
    path('update-teacher/<int:pk>', views.admin_update_teacher_view, name='update-teacher'),
    path('delete-teacher/<int:pk>', views.admin_delete_teacher_view, name='delete-teacher'),
    path('admin-add-branch/', views.admin_add_branch_view, name='admin-add-branch'),
path('admin-add-course/', views.admin_add_course_view, name='admin-add-course'),
path('admin-view-course/', views.admin_view_course_view, name='admin-view-course'),
    path('delete-course/<int:pk>', views.admin_delete_course_view, name='delete-course'),
    path('delete-question/<int:pk>', views.delete_question_view, name='delete-question'),
    path('admin-reset-exam/<int:pk>/', views.admin_reset_exam_view, name='admin-reset-exam'),
    path('admin-students-pending/', views.admin_students_pending, name='admin-students-pending'),
    path('approve-student/<int:id>/', views.admin_approve_student, name='approve-student'),
    path('reject-student/<int:id>/', views.admin_reject_student, name='reject-student'),
    path('admin-bulk-student-action/', views.admin_bulk_student_action, name='admin-bulk-student-action'),
    path('teacher/', include(('teacher.urls', 'teacher'), namespace='teacher')),
    path('student/', include(('student.urls', 'student'), namespace='student')),
    path('pricing/', views.pricing, name='pricing'),
    path('aboutus/', views.aboutus_view, name='aboutus'),
    path('contactus/', views.contactus_view, name='contactus'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)