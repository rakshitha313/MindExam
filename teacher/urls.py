from django.urls import path
from teacher import views
from django.contrib.auth.views import LoginView
app_name = 'teacher'   # 👈 ADD THIS LINE (VERY IMPORTANT)
urlpatterns = [

# -----------------------
# Authentication
# -----------------------


path('teachersignup/', views.teacher_signup_view, name='teachersignup'),


# -----------------------
# Dashboard
# -----------------------

 path('teacher-dashboard/', views.teacher_dashboard_view, name='teacher-dashboard'),


# -----------------------
# Course Management
# -----------------------

path(
    'teacher-exam/',
    views.teacher_exam_view,
    name='teacher-exam'
),

path(
    'teacher-add-exam/',
    views.teacher_add_exam_view,
    name='teacher-add-exam'
),

path(
    'teacher-view-exam/',
    views.teacher_view_exam_view,
    name='teacher-view-exam'
),
path('publish-exam/<int:pk>/', views.teacher_publish_exam, name='publish-exam'),
path('edit-exam/<int:pk>/', views.edit_exam_view, name='edit-exam'),
path('delete-exam/<int:pk>/', views.delete_exam_view, name='delete-exam'),

path(
    'teacher-manage-course/',
    views.teacher_manage_course,
    name='teacher-manage-course'
),

# path(
#     'edit-course/<int:pk>/',
#     views.edit_course_view,
#     name='edit-course'
# ),
# path('delete-course/<int:pk>/', views.delete_course_view, name='delete-course'),
path(
    'create-exam/',
    views.teacher_create_exam_view,
    name='create-exam'
),

path(
    'create-exam-success/<int:pk>/',
    views.teacher_exam_success_view,
    name='teacher-exam-success'
),


# -----------------------
# Question Management
# -----------------------

path(
    'teacher-question/',
    views.teacher_question_view,
    name='teacher-question'
),
path('teacher-add-question/', views.teacher_add_question_view, name='teacher-add-question'),



path(
    'teacher-view-question/',
    views.teacher_view_question_view,
    name='teacher-view-question'
),

path(
    'teacher-manage-question/',
    views.teacher_manage_question_view,
    name='teacher-manage-question'
),

path('see-question/<int:pk>/', views.see_question_view, name='see-question'),

path(
    'view-question-detail/<int:pk>/',
    views.teacher_view_question_detail_view,
    name='view-question-detail'
),

path(
    'edit-question/<int:pk>/',
    views.teacher_edit_question_view,
    name='edit-question'
),

path(
    'remove-question/<int:pk>/',
    views.remove_question_view,
    name='remove-question'
),


# -----------------------
# Student Management
# -----------------------

path(
    'teacher-student/',
    views.teacher_student_view,
    name='teacher-student'
),

path(
    'teacher-view-student/',
    views.teacher_view_student_view,
    name='teacher-view-student'
),


# -----------------------
# Notifications
# -----------------------

path(
    'notifications/',
    views.teacher_notifications_view,
    name='teacher-notifications'
),

path(
    'teacher-doubts/',
    views.teacher_doubts_view,
    name='teacher-doubts'
),

path(
    'teacher-resolve-doubt/<int:pk>/',
    views.teacher_resolve_doubt_view,
    name='teacher-resolve-doubt'
),


# -----------------------
# Teacher Settings
# -----------------------

path(
    'settings/',
    views.teacher_settings_view,
    name='teacher-settings'
),

]