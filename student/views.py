from django.shortcuts import render,redirect,reverse,get_object_or_404
from . import forms,models
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL
import random

from student.models import StudentAnswer
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from exam.models import Question, Course

from django.contrib.auth import authenticate, login
from exam.models import Course, Exam, Result
from student.models import Student

from student import models as SMODEL
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from exam.models import Admin
from django.db.models import Avg, Max, Sum
from student.forms import StudentUserForm, StudentForm
#for showing signup/login button for student
from django.contrib.auth.models import User
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def student_signup_view(request):
    if request.method == 'POST':
        userForm = StudentUserForm(request.POST)
        studentForm = StudentForm(request.POST, request.FILES)

        if userForm.is_valid() and studentForm.is_valid():

            username = userForm.cleaned_data.get('username')
            email = userForm.cleaned_data.get('email')
            password = userForm.cleaned_data.get('password')

            admin = studentForm.cleaned_data.get('admin')
            branch = studentForm.cleaned_data.get('branch')
            course = studentForm.cleaned_data.get('course')

            # username duplicate check
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Try another one.")
                return render(request, 'student/studentsignup.html', {
                    'userForm': userForm,
                    'studentForm': studentForm
                })

            # extra safety: course must belong to selected institution
            if course and admin and course.admin != admin:
                messages.error(request, "Selected course does not belong to selected institution.")
                return render(request, 'student/studentsignup.html', {
                    'userForm': userForm,
                    'studentForm': studentForm
                })

            # extra safety: course must belong to selected branch
            if course and branch and course.branch != branch:
                messages.error(request, "Selected course does not belong to selected branch.")
                return render(request, 'student/studentsignup.html', {
                    'userForm': userForm,
                    'studentForm': studentForm
                })

            # create user
            user = userForm.save(commit=False)
            user.email = email
            user.set_password(password)
            user.save()

            # create student profile
            student = studentForm.save(commit=False)
            student.user = user
            student.admin = admin
            student.branch = branch
            student.course = course
            student.save()

            # add to STUDENT group
            group, created = Group.objects.get_or_create(name='STUDENT')
            user.groups.add(group)

            messages.success(request, "Account created successfully! Wait for admin approval.")
            return redirect('login')

        else:
            print("USER FORM ERRORS:", userForm.errors)
            print("STUDENT FORM ERRORS:", studentForm.errors)
            messages.error(request, "Please correct the errors below.")

    else:
        userForm = StudentUserForm()
        studentForm = StudentForm()

    return render(request, 'student/studentsignup.html', {
        'userForm': userForm,
        'studentForm': studentForm
    })


@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def student_dashboard_view(request):

    # 🔹 Get logged-in student
    student = SMODEL.Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found")
        return redirect('login')

    # 🔹 Safety check
    if not student.branch or not student.course:
        messages.warning(request, "Branch or Course not assigned. Contact admin.")

    # 🔹 Get admin (institution)
    admin = student.admin
    institution_name = admin.institution_name if admin else "Not Assigned"

    # 🔹 Stats (filtered by student branch)
    total_course = QMODEL.Course.objects.filter(
        admin=admin,
        branch=student.branch
    ).count() if admin and student.branch else 0

    total_question = QMODEL.Question.objects.filter(
        admin=admin,
        exam__course__branch=student.branch
    ).count() if admin and student.branch else 0

    # 🔹 Results
    results = QMODEL.Result.objects.filter(student=student)

    if admin:
        results = results.filter(admin=admin)

    total_attempted = results.count()
    avg_score = results.aggregate(Avg('marks'))['marks__avg'] or 0
    highest_score = results.aggregate(Max('marks'))['marks__max'] or 0
    certificate_count = results.filter(marks__gte=50).count()

    # 🔹 Leaderboard
    leaderboard = QMODEL.Result.objects.filter(
        admin=admin
    ).values('student__id').annotate(
        total=Sum('marks')
    ).order_by('-total') if admin else []

    rank = None
    for i, l in enumerate(leaderboard):
        if l['student__id'] == student.id:
            rank = i + 1
            break

    # 🔹 Recent activity
    recent_results = results.order_by('-date')[:5]

    scores = list(results.values_list('marks', flat=True))
    dates = list(results.values_list('date', flat=True))

    # 🔹 UPCOMING EXAMS (BRANCH + COURSE FILTERED)
    now = timezone.now()

    if student.branch and student.course:
        future_exams = QMODEL.Exam.objects.filter(
            status='Approved',
            admin=admin,
            course=student.course,
            course__branch=student.branch,
            start_time__gt=now
        )
    else:
        future_exams = QMODEL.Exam.objects.none()

    # 🔥 Optimized: remove already attempted exams
    attempted_exam_ids = QMODEL.Result.objects.filter(
        student=student
    ).values_list('exam_id', flat=True)

    upcoming_exams = future_exams.exclude(id__in=attempted_exam_ids)

    # 🔹 Context
    context = {
        'student': student,
        'admin': admin,
        'institution_name': institution_name,

        'total_course': total_course,
        'total_question': total_question,

        'total_attempted': total_attempted,
        'avg_score': avg_score,
        'highest_score': highest_score,
        'certificate_count': certificate_count,

        'rank': rank,
        'recent_results': recent_results,

        'scores': scores,
        'dates': dates,

        'upcoming_exams': upcoming_exams,
    }

    return render(request, 'student/student_dashboard.html', context)
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def student_exam_view(request):

    student = get_object_or_404(Student, user=request.user)

    # 🔒 Safety check
    if not student.branch or not student.course:
        messages.error(request, "Branch or Course not assigned")
        return redirect('student:student-dashboard')

    # ✅ FILTERED EXAMS
    exams = QMODEL.Exam.objects.filter(
        status='Approved',
        admin=student.admin,
        course=student.course,
        course__branch=student.branch
    ).order_by('-id')

    results = QMODEL.Result.objects.filter(student=student)

    attempted_exam_ids = results.values_list('exam_id', flat=True)

    return render(request, 'student/student_exam.html', {
        'exams': exams,
        'results': results,
        'student': student,
        'attempted_exam_ids': list(attempted_exam_ids)
    })

@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def start_exam_view(request, pk):

    student = get_object_or_404(Student, user=request.user)
    exam = get_object_or_404(
    QMODEL.Exam,
    id=pk,
    status='Approved',
    admin=student.admin,
    course=student.course,
    course__branch=student.branch
)

    if exam.status != 'Approved':
        messages.error(request, "Exam not approved.")
        return redirect('student:student-exam')

    attempts = Result.objects.filter(student=student, exam=exam).count()
    if attempts >= 3:
        messages.error(request, "Maximum attempts reached.")
        return redirect('student:student-exam')

    questions = list(QMODEL.Question.objects.filter(exam=exam).order_by('?'))

    if not questions:
        messages.error(request, "No questions found.")
        return redirect('student:student-exam')

    # ✅ store session safely
    request.session['exam_id'] = exam.id
    request.session['question_ids'] = [q.id for q in questions]

    return render(request, 'student/start_exam.html', {
        'exam': exam,
        'questions': questions,
        'total_questions': len(questions),
        'total_marks': sum(q.marks for q in questions),
        'attempts_left': 3 - attempts,
    })
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def verify_exam_access(request, pk):

    exam = get_object_or_404(
    QMODEL.Exam,
    id=pk,
    status='Approved',
    admin=student.admin,
    course=student.course,
    course__branch=student.branch
)
    student = SMODEL.Student.objects.filter(user=request.user).first()
    if not student:
     return redirect('login')

    attempts = QMODEL.Result.objects.filter(student=student, exam=exam).count()

    if attempts >= 10:
        return render(request, 'student/already_attempted.html', {
            'course': exam.course
        })

    # redirect to start exam
    return redirect('student:start_exam', pk=exam.id)
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def take_exam_view(request, pk):

    student = Student.objects.filter(user=request.user).first()
    if not student:
        return redirect('login')

    if not student.branch or not student.course:
        messages.error(request, "Your branch or course is not assigned.")
        return redirect('student:student-dashboard')

    exam = QMODEL.Exam.objects.filter(
        id=pk,
        status='Approved',
        course=student.course,
        course__branch=student.branch
    ).first()

    if not exam:
        messages.error(request, "You are not allowed to access this exam.")
        return redirect('student:student-dashboard')

    attempts = Result.objects.filter(student=student, exam=exam).count()

    return redirect('student:start_exam', pk=exam.id)
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def calculate_marks_view(request):

    if request.method != "POST":
        return redirect('student:student-dashboard')

    exam_id = request.session.get('exam_id')

    if not exam_id:
        messages.error(request, "Session expired. Retake exam.")
        return redirect('student:student-exam')

    exam = get_object_or_404(QMODEL.Exam, id=exam_id)
    student = get_object_or_404(Student, user=request.user)

    # 🔥 IMPORTANT: prevent duplicate submission
    if Result.objects.filter(student=student, exam=exam).exists():
        messages.error(request, "You already submitted this exam.")
        return redirect('student:student-dashboard')

    question_ids = request.session.get('question_ids', [])

    questions = QMODEL.Question.objects.filter(id__in=question_ids)

    total_marks = 0

    StudentAnswer.objects.filter(student=student, exam=exam).delete()

    for q in questions:
        selected = request.POST.get(str(q.id))

        if selected == q.answer:
            total_marks += q.marks

        StudentAnswer.objects.create(
            student=student,
            exam=exam,
            question=q,
            selected_answer=selected
        )

    result = Result.objects.create(
        student=student,
        exam=exam,
        marks=total_marks,
        admin=exam.admin
    )

    # cleanup session
    request.session.pop('exam_id', None)
    request.session.pop('question_ids', None)

    return redirect('student:check-marks', pk=result.id)
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def view_result_view(request):
    
    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found")
        return redirect('login')

    results = Result.objects.filter(student=student)

    return render(request,'student/view_result.html',{
        'results': results,
        'student': student
    })
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def check_marks_view(request, pk):

    student = SMODEL.Student.objects.filter(user=request.user).first()
    if not student:
        return redirect('login')

    # 🔥 pk is RESULT ID
    result = Result.objects.filter(id=pk, student=student).first()

    if not result:
        messages.error(request, "Result not found!")
        return redirect('student:student-dashboard')

    exam = result.exam

    attempts = Result.objects.filter(student=student, exam=exam).count()

    return render(request, 'student/check_marks.html', {
        'result': result,
        'exam': exam,
        'student': student,
        'attempts': attempts
    })
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def student_marks_view(request):

    student = models.Student.objects.filter(user=request.user).first()
    if not student:
      return redirect('login')

    results = Result.objects.filter(student=student).order_by('-date')

    return render(request,'student/student_marks.html',{
        'results':results
    })
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def student_leaderboard_view(request):

    leaders = QMODEL.Result.objects.select_related(
        'student__user'
    ).values(
        'student__user__first_name',
        'student__profile_pic'
    ).annotate(
        total_marks=Sum('marks')
    ).order_by('-total_marks')[:10]

    student = Student.objects.filter(user=request.user).first()
    return render(request,'student/leaderboard.html',{
        'leaders':leaders,
        'student': student
    })
    
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def course_leaderboard_view(request, pk):
    
    course = QMODEL.Course.objects.get(id=pk)

    exam = QMODEL.Exam.objects.filter(course=course).first()

    leaders = QMODEL.Result.objects.filter(
        exam=exam
    ).values(
        'student__user__first_name',
        'student__profile_pic'
    ).annotate(
        total_marks=Sum('marks')
    ).order_by('-total_marks')[:10]

    return render(request,'student/course_leaderboard.html',{
        'leaders':leaders,
        'course':course
    })
    
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def practice_exam_view(request):

    questions = QMODEL.Question.objects.order_by('?')[:10]

    return render(request,'student/practice_exam.html',{
        'questions':questions
    })
    
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def notifications_view(request):

    student = models.Student.objects.filter(user=request.user).first()
    if not student:
     return redirect('login')

    notifications = models.Notification.objects.filter(student=student).order_by('-created')

    return render(request,'student/notifications.html',{
        'notifications':notifications
    })

@login_required(login_url='login')
def certificate_view(request, pk):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect('student:student-dashboard')

    # 🔥 IMPORTANT FIX: filter by BOTH id and student
    result = get_object_or_404(Result, id=pk, student=student)

    context = {
        'course': result.exam.course,
        'student': student,
        'marks': result.marks,
        'result': result,
        'date': result.date,
    }

    return render(request, 'student/certificate.html', context)

@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def review_exam_view(request, pk):

    student = Student.objects.filter(user=request.user).first()
    if not student:
        return redirect('login')

    # ✅ result id
    result = get_object_or_404(Result, id=pk, student=student)

    exam = result.exam
    questions = QMODEL.Question.objects.filter(exam=exam)

    # ✅ GET STUDENT ANSWERS
    answers = StudentAnswer.objects.filter(student=student, exam=exam)

    # ✅ CONVERT TO DICTIONARY
    answer_dict = {a.question_id: a.selected_answer for a in answers}

    return render(request, 'student/review_exam.html', {
        'exam': exam,
        'questions': questions,
        'result': result,
        'answer_dict': answer_dict   # 🔥 IMPORTANT
    })
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def edit_profile_view(request):

    student = Student.objects.filter(user=request.user).first()
    if not student:
     return redirect('login')
    courses = Course.objects.all()

    if request.method == 'POST':
        student.mobile = request.POST.get('mobile')
        student.address = request.POST.get('address')

        course_id = request.POST.get('course')
        student.course = Course.objects.get(id=course_id)

        # ✅ Profile image upload
        if 'profile_pic' in request.FILES:
            student.profile_pic = request.FILES['profile_pic']

        student.save()

        return redirect('student:student-dashboard')   # ✅ FIXED

    # ✅ VERY IMPORTANT (for GET request)
    return render(request, 'student/edit_profile.html', {
        'student': student,
        'courses': courses
    })
def student_doubts(request):
    student = SMODEL.Student.objects.filter(user=request.user).first()
    if not student:
     return redirect('login')
    if request.method == 'POST':
        question = request.POST.get('question')
        course_id = request.POST.get('course')
        course = QMODEL.Course.objects.get(id=course_id) if course_id else None
        
        SMODEL.Doubt.objects.create(
            student=student,
            course=course,
            question=question
        )
        messages.success(request, "Your inquiry has been submitted to the faculty.")
        return redirect('student:student-doubts')

    doubts = SMODEL.Doubt.objects.filter(student=student).order_by('-created_at')
    courses = QMODEL.Course.objects.all()
    
    return render(request, 'student/student_doubts.html', {
        'doubts': doubts,
        'student': student,
        'courses': courses
    })

def bookmark_question(request,pk):
    
    student = SMODEL.Student.objects.get(user=request.user)
    question = QMODEL.Question.objects.get(id=pk)

    QMODEL.Bookmark.objects.get_or_create(
        student=student,
        question=question
    )

    return redirect(request.META.get('HTTP_REFERER'))
from django.contrib import messages

@login_required
def student_settings_view(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return redirect('login')

    if request.method == "POST":
        user = request.user

        # update user info
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        # ✅ REMOVE IMAGE
        if request.POST.get("remove_pic"):
            if student.profile_pic:
                student.profile_pic.delete(save=False)
            student.profile_pic = None
            student.save()

        # ✅ UPLOAD IMAGE
        elif request.FILES.get("profile_pic"):
            student.profile_pic = request.FILES["profile_pic"]
            student.save()

        # password change
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 and password1 == password2:
            user.set_password(password1)
            update_session_auth_hash(request, user)

        user.save()

        messages.success(request, "Profile updated successfully ✅")
        return redirect("student:student-settings")

    return render(request, 'student/settings.html', {'student': student})
@login_required(login_url='login')
@user_passes_test(is_student, login_url='login')
def sustainable_travel_view(request):
    student = Student.objects.get(user=request.user)
    return render(request, 'student/sustainable_travel.html', {'student': student})

    
    
