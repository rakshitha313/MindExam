# exam/views.py
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q, Avg, Max
from django.db import models
from django.contrib.auth.models import Group
from .models import Exam, Course, Result, Question
from student.models import Student, Notification
from teacher import models as TMODEL

from teacher import forms as TFORM
from student import forms as SFORM
import uuid
from teacher.models import Teacher
from exam import models as QMODEL
from django.contrib.auth.forms import PasswordChangeForm
from exam.models import Admin
from .forms import BranchForm, CourseForm, QuestionForm, AdminUserForm
from django.shortcuts import get_object_or_404
from student.forms import StudentUserForm, StudentForm
from django.core.mail import send_mail
from django.conf import settings
def is_teacher(user): return user.groups.filter(name='TEACHER').exists()
def is_student(user): return user.groups.filter(name='STUDENT').exists()
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='ADMIN').exists()


def home_view(request):
    return render(request, 'exam/index.html')

def portal_view(request):
    return render(request, 'portal.html')

def login_view(request):

    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # ================= STUDENT =================
            if role == "student":
                if Student.objects.filter(user=user).exists():

                    student = Student.objects.get(user=user)

                    # 🚨 Approval check
                    if not student.is_approved:
                        messages.error(request, "⏳ Your account is waiting for admin approval")
                        return redirect('login')

                    login(request, user)
                    messages.success(request, "✅ Student login successful")
                    return redirect('student:student-dashboard')

                else:
                    messages.error(request, "❌ This account is not a Student")

            # ================= TEACHER =================
            elif role == "teacher":
                if Teacher.objects.filter(user=user).exists():

                    login(request, user)
                    messages.success(request, "✅ Teacher login successful")
                    return redirect('teacher:teacher-dashboard')

                else:
                    messages.error(request, "❌ This account is not a Teacher")

            # ================= ADMIN =================
            elif role == "admin":
                if Admin.objects.filter(user=user).exists():

                    login(request, user)
                    messages.success(request, "✅ Institution login successful")
                    return redirect('admin-dashboard')

                else:
                    messages.error(request, "❌ This account is not an Institution")

        else:
            messages.error(request, "❌ Invalid username or password")

    return render(request, "login.html")
def afterlogin_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    # DEBUG: check which groups the user belongs to
    print("User:", user.username)
    print("Groups:", [g.name for g in user.groups.all()])

    if user.groups.filter(name='ADMIN').exists():
        return redirect('admin-dashboard')
    elif user.groups.filter(name='TEACHER').exists():
        return redirect('teacher:teacher-dashboard')
    elif user.groups.filter(name='STUDENT').exists():
        return redirect('student:student-dashboard')
    else:
        messages.error(request, "You do not have a valid role assigned. Contact admin.")
        logout(request)
        return redirect('login')
def logout_view(request):
    logout(request)
    return redirect('/')

# ---------------------------------------------------------------------------------
# ADMINISTRATIVE COMMAND CENTER (ADMIN)
# ---------------------------------------------------------------------------------
def get_admin(request):
    return Admin.objects.filter(user=request.user).first()

    
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_dashboard_view(request):

    admin = get_admin(request)

    if not admin:
        logout(request)
        messages.error(request, "Unauthorized access ❌")
        return redirect('login')

    # Counts
    total_students = Student.objects.filter(admin=admin).count()
    approved_students = Student.objects.filter(admin=admin, is_approved=True).count()
    pending_students_count = Student.objects.filter(
        admin=admin,
        is_approved=False,
        is_rejected=False
    ).count()
    rejected_students = Student.objects.filter(admin=admin, is_rejected=True).count()

    teachers = TMODEL.Teacher.objects.filter(admin=admin)
    courses = Course.objects.filter(admin=admin)
    questions = Question.objects.filter(admin=admin)

    pending_exams = Exam.objects.filter(admin=admin, status='Pending')

    pending_students = Student.objects.filter(
        admin=admin,
        is_approved=False,
        is_rejected=False
    )

    return render(request, 'exam/admin_dashboard.html', {
        'total_student': approved_students,   # ✅ show only approved
        'total_teacher': teachers.count(),
        'total_course': courses.count(),
        'total_question': questions.count(),

        'pending_exams': pending_exams,
        'pending_students': pending_students,

        # optional (for UI upgrade)
        'approved_students': approved_students,
        'pending_students_count': pending_students_count,
        'rejected_students': rejected_students,
        'total_students': total_students,
    })
    
from .models import Branch

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_add_branch_view(request):

    form = BranchForm()

    if request.method == 'POST':
        form = BranchForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Branch added successfully")
            return redirect('admin-add-branch')

    branches = Branch.objects.all()

    return render(request, 'exam/admin_add_branch.html', {
        'form': form,
        'branches': branches
    })
# --- Faculty Management ---
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_teacher_view(request):
    admin = get_admin(request)
    return render(request, 'exam/admin_teacher.html', {
    'total_teacher': TMODEL.Teacher.objects.filter(admin=admin).count()
})
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_view_teacher_view(request):
    admin = get_admin(request)
    teachers = TMODEL.Teacher.objects.filter(admin=admin)
    return render(request, 'exam/admin_view_teacher.html', {'teachers': teachers})
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_add_teacher_view(request):

    if request.method == 'POST':
        userForm = TFORM.TeacherUserForm(request.POST)
        teacherForm = TFORM.TeacherAdminForm(request.POST, request.FILES)

        if userForm.is_valid() and teacherForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()

            admin = get_admin(request)

            teacher = teacherForm.save(commit=False)
            teacher.user = user
            teacher.admin = admin   # ✅ auto assign
            teacher.save()

            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name='TEACHER')
            group.user_set.add(user)

            messages.success(request, "Faculty Unit Registered Successfully")
            return redirect('admin-view-teacher')

    else:
        userForm = TFORM.TeacherUserForm()
        teacherForm = TFORM.TeacherAdminForm()   # ✅ FIXED HERE

    return render(request, 'exam/admin_add_teacher.html', {
        'userForm': userForm,
        'teacherForm': teacherForm
    })
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_view_pending_teacher_view(request):
    return render(request, 'exam/admin_view_pending_teacher.html', {'teachers': TMODEL.Teacher.objects.filter(status=False)})
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='adminlogin')
def admin_view_teacher_salary_view(request):
    return render(request, 'exam/admin_view_teacher_salary.html', {'teachers': TMODEL.Teacher.objects.all()})

# --- Candidate Management ---
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_student_view(request):
    admin = get_admin(request)

    return render(request, 'exam/admin_student.html', {
        'total_student': Student.objects.filter(
            admin=admin,
            is_approved=True   # ✅ FIX
        ).count()
    })

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_view_student_view(request):
    admin = get_admin(request)

    students = Student.objects.filter(
        admin=admin,          # ✅ FILTER BY ADMIN
        is_approved=True      # ✅ ONLY APPROVED
    )

    return render(request, 'exam/admin_view_student.html', {
        'students': students
    })
    



# 📌 SHOW PENDING STUDENTS
def admin_students_pending(request):
    admin = get_admin(request)

    students = Student.objects.filter(
        admin=admin,
        is_approved=False,
        is_rejected=False
    )

    return render(request, 'exam/admin_pending_students.html', {'students': students})


# ✅ APPROVE STUDENT
def admin_approve_student(request, id):
    student = get_object_or_404(Student, id=id)

    student.is_approved = True
    student.is_rejected = False
    student.save()

    send_mail(
        subject="Account Approved 🎉",
        message=f"Hi {student.user.first_name}, your account has been approved.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[student.user.email],
        fail_silently=True,
    )

    messages.success(request, "Student approved successfully")
    return redirect('admin-students-pending')


# ❌ REJECT STUDENT
def admin_reject_student(request, id):
    student = get_object_or_404(Student, id=id)

    student.is_rejected = True
    student.is_approved = False
    student.save()

    send_mail(
        subject="Account Rejected ❌",
        message=f"Hi {student.user.first_name}, your registration was rejected.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[student.user.email],
        fail_silently=True,
    )

    messages.error(request, "Student rejected successfully")
    return redirect('admin-students-pending')
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_course_view(request):
    return render(request, 'exam/admin_course.html', {'total_course': Course.objects.count()})

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')

def admin_view_course_view(request):
    admin = get_admin(request)

    courses = Course.objects.filter(admin=admin)

    # attach exams to each course
    for course in courses:
        course.exams = Exam.objects.filter(course=course)

    return render(request, 'exam/admin_view_course.html', {
        'courses': courses
    })
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_add_course_view(request):
    admin = get_admin(request)

    courseForm = CourseForm(admin=admin)

    if request.method == 'POST':
        courseForm = CourseForm(request.POST, admin=admin)

        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.admin = admin
            course.save()

            messages.success(request, "Course added successfully")
            return redirect('admin-view-course')

    return render(request, 'exam/admin_add_course.html', {
        'courseForm': courseForm
    })

# --- Question Management ---
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_question_view(request):
    admin = get_admin(request)
    total_question = Question.objects.filter(admin=admin).count()
    return render(request, 'exam/admin_question.html', {'total_question': total_question})
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_view_question_view(request, exam_id):

    admin = get_admin(request)

    questions = Question.objects.filter(
        admin=admin,
        exam_id=exam_id   # 🔥 important filter
    )

    return render(request, 'exam/admin_view_question.html', {
        'questions': questions
    })

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_add_question_view(request):
    questionForm = QuestionForm()
    if request.method == 'POST':
        questionForm = QuestionForm(request.POST)
        if questionForm.is_valid():
            admin = get_admin(request)   # ✅ ADD THIS

            question = questionForm.save(commit=False)
            question.admin = admin       # ✅ VERY IMPORTANT
            question.save()

            return redirect('admin-view-question')

    return render(request, 'exam/admin_add_question.html', {'questionForm': questionForm})

# --- Outcomes & Analytics ---
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_view_results_view(request):
    admin = get_admin(request)

    if not admin:
        messages.error(request, "Admin not found!")
        return redirect('admin-dashboard')

    results = Result.objects.filter(admin=admin)

    print("ADMIN:", admin)
    print("RESULT COUNT:", results.count())

    return render(request, 'exam/admin_view_results.html', {
        'results': results
    })
@login_required(login_url='adminlogin')
@user_passes_test(is_admin, login_url='login')
def admin_view_marks_view(request, pk):
    admin = get_admin(request)

    student = Student.objects.filter(id=pk, admin=admin).first()
    if not student:
        return redirect('admin-view-student')

    marks = Result.objects.filter(
        student=student,
        exam__admin=admin
    )
    print("STUDENT:", student)
    print("RESULTS:", Result.objects.filter(student=student))
    print("ALL RESULTS:", Result.objects.all())

    return render(request, 'exam/admin_view_marks.html', {
        'student': student,
        'marks': marks
    })
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_check_marks_view(request, pk):
    return render(request, 'exam/admin_check_marks.html', {'results': Result.objects.filter(exam_id=pk)})
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_view_pending_exams_view(request):
    admin = get_admin(request)
    pending_exams = Exam.objects.filter(admin=admin, status='Pending')
    return render(request, 'exam/admin_view_pending_exams.html', {'pending_exams': pending_exams})

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_conduct_exam_view(request):
    return render(request, 'exam/admin_conduct_exam.html')

# --- Administrative Actions ---
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_approve_exam_view(request, pk):
    try:
        admin = get_admin(request)
        exam = Exam.objects.get(id=pk, admin=admin)
        exam.status = 'Approved'
        exam.save()
        messages.success(request, "Status Updated Successfully")
        messages.success(request, "Exam is now Active for Students")
    except: pass
    return redirect('admin-dashboard')
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_reject_exam_view(request, pk):
    try:
        admin = get_admin(request)
        exam = Exam.objects.get(id=pk, admin=admin)
        exam.status = 'Rejected'
        exam.save()
        messages.warning(request, f"Exam '{exam.exam_name}' has been rejected.")
    except: pass
    return redirect('admin-dashboard')

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def delete_question_view(request, pk):
    try:
        admin = get_admin(request)
        Question.objects.get(id=pk, admin=admin).delete()
    except: pass
    return redirect('admin-view-question')

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_approve_teacher_view(request, pk):
    try:
        admin = get_admin(request)
        teacher = get_object_or_404(TMODEL.Teacher, id=pk, admin=admin)
        teacher.status = True
        teacher.save()
        messages.success(request, f"Faculty {teacher.get_name} authenticated successfully.")
    except Exception as e:
     print("ERROR:", e)
     messages.error(request, "Teacher not found or already removed")
    return redirect('admin-view-pending-teacher')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_reject_teacher_view(request, pk):

    admin = get_admin(request)

    teacher = TMODEL.Teacher.objects.filter(id=pk).first()

    if not teacher:
        messages.error(request, "Teacher not found")
        return redirect('admin-view-pending-teacher')

    # IMPORTANT CHECK
    if teacher.admin != admin:
        messages.error(request, "You are not allowed to delete this teacher")
        return redirect('admin-view-pending-teacher')

    user = teacher.user
    teacher.delete()
    user.delete()

    messages.warning(request, "Faculty application declined and removed.")
    return redirect('admin-view-pending-teacher')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_delete_teacher_view(request, pk):
    try:
        admin = get_admin(request)
        teacher = TMODEL.Teacher.objects.get(id=pk, admin=admin)
        user = teacher.user
        teacher.delete()
        user.delete()
        messages.info(request, "Faculty decommissioned successfully.")
    except: pass
    return redirect('admin-view-teacher')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_update_teacher_view(request, pk):

    admin = get_admin(request)
    teacher = TMODEL.Teacher.objects.get(id=pk, admin=admin)
    user = teacher.user

    userForm = TFORM.TeacherUserForm(instance=user)
    teacherForm = TFORM.TeacherAdminForm(instance=teacher)   # ✅ FIX

    if request.method == 'POST':
        userForm = TFORM.TeacherUserForm(request.POST, instance=user)
        teacherForm = TFORM.TeacherAdminForm(request.POST, request.FILES, instance=teacher)  # ✅ FIX

        if userForm.is_valid() and teacherForm.is_valid():
            user = userForm.save(commit=False)

            # ✅ Better password handling
            password = userForm.cleaned_data.get('password')
            if password:
                user.set_password(password)

            user.save()
            teacherForm.save()   # admin stays same ✅

            messages.success(request, "Faculty configuration updated.")
            return redirect('admin-view-teacher')

    return render(request, 'exam/update_teacher.html', {
        'userForm': userForm,
        'teacherForm': teacherForm
    })

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_delete_course_view(request, pk):
    try:
        admin = get_admin(request)
        Course.objects.get(id=pk, admin=admin).delete()
        messages.info(request, "Curriculum track terminated.")
    except: pass
    return redirect('admin-view-course')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_reset_exam_view(request, pk):
    try:
        admin = get_admin(request)
        Result.objects.filter(id=pk, admin=admin).delete()
        messages.success(request, "Candidate session reset successfully.")
    except: pass
    return redirect('admin-view-results')

def admin_signup_view(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)

        if form.is_valid():

            # ✅ Create user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True
            user.save()

            # ✅ Create admin profile
            Admin.objects.create(
                user=user,
                institution_name=form.cleaned_data['institution_name']
            )

            # ✅ Assign ADMIN group
            group, _ = Group.objects.get_or_create(name='ADMIN')
            user.groups.add(group)

            messages.success(request, "Institution registered successfully. Please login.")
            return redirect('login')

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = AdminUserForm(request.POST)

    return render(request, 'exam/adminsignup.html', {'form': form})


def aboutus_view(request): return render(request, 'exam/aboutus.html')
def contactus_view(request): return render(request, 'exam/contactus.html')
def calculate_marks_view(request): return redirect('student:student-dashboard')


@login_required(login_url='login')
@user_passes_test(is_admin)
def update_student_view(request, pk):
    admin = get_admin(request)

    student = get_object_or_404(Student, id=pk, admin=admin)
    user = student.user

    if request.method == 'POST':

        userForm = StudentUserForm(request.POST, instance=user)
        studentForm = StudentForm(request.POST, request.FILES, instance=student)

        if userForm.is_valid() and studentForm.is_valid():

            # ---- USER SAVE ----
            user = userForm.save(commit=False)

            password = userForm.cleaned_data.get('password')
            if password:
                user.set_password(password)

            user.save()

            # ---- STUDENT SAVE (IMPORTANT FIX) ----
            student = studentForm.save(commit=False)
            student.admin = admin   # 🔥 FIX FOR ERROR
            student.save()

            messages.success(request, "Student updated successfully")
            return redirect('admin-view-student')

        else:
            print("USER FORM ERRORS:", userForm.errors)
            print("STUDENT FORM ERRORS:", studentForm.errors)

            messages.error(request, "Please correct the errors")

    else:
        userForm = StudentUserForm(instance=user)
        studentForm = StudentForm(instance=student)

    return render(request, 'exam/update_student.html', {
        'userForm': userForm,
        'studentForm': studentForm
    })
@login_required(login_url='login')
@user_passes_test(is_admin)
def delete_student_view(request, pk):
    admin = get_admin(request)
    student = Student.objects.get(id=pk, admin=admin)
    student.delete()
    messages.success(request, "Student deleted successfully")
    return redirect('admin-view-student')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_settings_view(request):

    user = request.user
    admin = Admin.objects.filter(user=user).first()

    if request.method == 'POST':

        # UPDATE USER INFO
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        # PROFILE IMAGE (OPTIONAL)
        profile_pic = request.FILES.get('profile_pic', None)

        if profile_pic and admin:
            admin.profile_pic = profile_pic
            admin.save()

        # PASSWORD UPDATE
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password and confirm_password:
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Password updated successfully")
                return redirect('login')  # important after password change
            else:
                messages.error(request, "Passwords do not match")
                return redirect('admin-settings')

        messages.success(request, "Profile updated successfully")
        return redirect('admin-settings')

    return render(request, 'exam/admin_settings.html', {
        'admin': admin
    })
def pricing(request):
    return render(request, 'pricing.html')
from django.shortcuts import redirect
from student.models import Student

def admin_bulk_student_action(request):
    if request.method == "POST":
        action = request.POST.get("action")
        student_ids = request.POST.getlist("students")

        admin = get_admin(request)  # IMPORTANT

        if action == "approve":
            Student.objects.filter(
                id__in=student_ids,
                admin=admin
            ).update(is_approved=True)

        elif action == "reject":
            Student.objects.filter(
                id__in=student_ids,
                admin=admin
            ).update(is_approved=False)

    return redirect('admin-dashboard')
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_view_course_view(request):
    admin = get_admin(request)

    courses = Course.objects.filter(admin=admin)

    for course in courses:
        course.exams = Exam.objects.filter(course=course)

    return render(request, 'exam/admin_view_course.html', {
        'courses': courses
    })