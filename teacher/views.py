from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import update_session_auth_hash
from exam.models import Admin
from teacher.models import Teacher
from exam.models import Course
from . import forms
from exam.forms import ExamForm
from django.contrib import messages
from django.contrib.auth.models import Group
from student import models as SMODEL
from exam import models as QMODEL
from . import models as TMODEL
from exam import forms as QFORM
from exam.models import Question
from exam.forms import CourseForm
from .utility import get_admin
from exam.forms import QuestionForm
from exam.models import Exam
from .forms import UploadExcelForm
import openpyxl
from exam.models import Exam, Question, Course 
from django.db.models import Count, Sum, Q
from teacher.forms import TeacherUserForm, TeacherForm
# ------------------------------------------------
# Check if user is teacher
# --------------------------------------------------

def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()


# --------------------------------------------------
# Teacher Click
# --------------------------------------------------


# --------------------------------------------------
# Teacher Signup
# --------------------------------------------------

# views.py

from django.contrib import messages

def teacher_signup_view(request):
    
    userForm = TeacherUserForm()
    teacherForm = TeacherForm()

    if request.method == 'POST':
        userForm = TeacherUserForm(request.POST)
        teacherForm = TeacherForm(request.POST, request.FILES)

        if userForm.is_valid() and teacherForm.is_valid():

            # ✅ Create user
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()

            # ✅ Create teacher profile
            teacher = teacherForm.save(commit=False)
            teacher.user = user

            # ✅ Institution (admin)
            teacher.admin = teacherForm.cleaned_data.get('admin')

            # ✅ OPTIONAL PROFILE IMAGE FIX
            if 'profile_pic' in request.FILES:
                teacher.profile_pic = request.FILES['profile_pic']
            else:
                teacher.profile_pic = None   # safe fallback

            # ✅ auto approve
            teacher.status = True

            teacher.save()

            # ✅ assign group
            group, _ = Group.objects.get_or_create(name='TEACHER')
            user.groups.add(group)

            messages.success(request, "Teacher registered successfully!")
            return redirect('teacherlogin')

        else:
            print(userForm.errors)
            print(teacherForm.errors)
            messages.error(request, "Please fix the errors")

    return render(request, 'teacher/teachersignup.html', {
        'userForm': userForm,
        'teacherForm': teacherForm
    })
# --------------------------------------------------
# Teacher Dashboard
# --------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_dashboard_view(request):
    teacher = TMODEL.Teacher.objects.get(user=request.user)
    admin = teacher.admin

    latest_exam = QMODEL.Exam.objects.filter(
        teacher=teacher
    ).order_by('-id').first()

    context = {
        'institution': admin.institution_name,

        # all courses in this institution
        'total_course': QMODEL.Course.objects.filter(admin=admin).count(),

        # only this teacher's questions
        'total_question': QMODEL.Question.objects.filter(
            exam__teacher=teacher
        ).count(),

        # all approved students in this institution
        'total_student': SMODEL.Student.objects.filter(
            admin=admin,
            is_approved=True
        ).count(),

        # doubts only from this institution
        'pending_doubts': SMODEL.Doubt.objects.filter(
            is_resolved=False,
            student__admin=admin
        ).count(),

        # only this teacher's exams
        'total_exam': QMODEL.Exam.objects.filter(
    teacher=teacher
).count(),

        'latest_exam': latest_exam
    }

    return render(request, 'teacher/teacher_dashboard.html', context)
# --------------------------------------------------
# Course Management
# --------------------------------------------------
@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_exam_view(request):
    return render(request, 'teacher/teacher_exam.html')


@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_add_exam_view(request):
    return redirect('teacher:teacher-create-exam')
# @login_required(login_url='login')
# @user_passes_test(is_teacher, login_url='login')
# def edit_course_view(request, pk):
#     course = get_object_or_404(QMODEL.Course, id=pk)
#     if request.method == 'POST':
#         courseForm = QFORM.CourseForm(request.POST, instance=course)
#         if courseForm.is_valid():
#             courseForm.save()
#             return redirect('teacher:teacher-view-exam')
#     else:
#         courseForm = QFORM.CourseForm(instance=course)
#     return render(request, 'teacher/edit_course.html', {'courseForm': courseForm, 'course': course})

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_create_exam_view(request):
    teacher = TMODEL.Teacher.objects.get(user=request.user)
    admin = teacher.admin

    if request.method == 'POST':
        examForm = QFORM.ExamForm(request.POST, admin=admin)

        if examForm.is_valid():
            exam = examForm.save(commit=False)
            exam.admin = admin
            exam.teacher = teacher
            exam.status = 'Pending'

            exam.save()

            messages.success(request, "Exam created successfully.")
            return redirect('teacher:teacher-exam-success', pk=exam.id)
    else:
        examForm = QFORM.ExamForm(admin=admin)

    return render(request, 'teacher/teacher_create_exam.html', {
        'examForm': examForm
    })
@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_exam_success_view(request, pk):
    exam = get_object_or_404(QMODEL.Exam, id=pk, teacher=request.user.teacher)
    return render(request, 'teacher/teacher_exam_success.html', {'exam': exam})


from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_view_exam_view(request):
    teacher = request.user.teacher
    admin = teacher.admin

    exams = Exam.objects.filter(
        admin=admin,
        teacher=teacher
    ).annotate(
        total_questions_calc=Count('question'),
        total_marks_calc=Coalesce(Sum('question__marks'), Value(0))
    )

    return render(request, 'teacher/teacher_view_exam.html', {
        'exams': exams
    })
@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def delete_exam_view(request, pk):
    exam = get_object_or_404(Exam, id=pk, teacher=request.user.teacher)
    exam.delete()
    return redirect('teacher:teacher-view-exam')

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def edit_exam_view(request, pk):
    exam = get_object_or_404(Exam, id=pk, teacher=request.user.teacher)

    teacher = request.user.teacher
    admin = teacher.admin

    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam, admin=admin)

        if form.is_valid():
            form.save()
            messages.success(request, "Updated successfully")
            return redirect('teacher:teacher-view-exam')
    else:
        form = ExamForm(instance=exam, admin=admin)

    return render(request, 'teacher/edit_exam.html', {
        'form': form,
        'exam': exam
    })
# --------------------------------------------------
# Question Management
# --------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_question_view(request):
    return render(request, 'teacher/teacher_question.html')


  # Adjust based on your Teacher model

  # if you use teacher relation directly


@login_required(login_url='login')
@user_passes_test(lambda u: u.groups.filter(name='TEACHER').exists(), login_url='login')
def teacher_add_question_view(request):
    teacher = getattr(request.user, "teacher", None)
    if not teacher:
        messages.error(request, "Teacher profile not found.")
        return redirect("login")

    admin = teacher.admin
    if not admin:
        messages.error(request, "Institution not found for this teacher.")
        return redirect("login")

    form = QuestionForm()
    form.fields['exam'].queryset = Exam.objects.filter(
    admin=admin,
    teacher=teacher
)

    def get_exam_progress(exam_obj):
        actual_questions = Question.objects.filter(exam=exam_obj).count()
        actual_marks = Question.objects.filter(exam=exam_obj).aggregate(
            total=Sum('marks')
        )['total'] or 0

        expected_questions = exam_obj.total_questions or 0
        expected_marks = exam_obj.total_marks or 0

        missing_questions = max(0, expected_questions - actual_questions)
        missing_marks = max(0, expected_marks - actual_marks)

        return actual_questions, actual_marks, missing_questions, missing_marks

    if request.method == "POST":

        # ================= EXCEL UPLOAD =================
        if request.FILES.get("file"):
            excel_file = request.FILES["file"]

            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active

                added_count = 0
                target_exam = None
                target_exam_name = None

                course = Course.objects.filter(admin=admin).first()
                if not course:
                    messages.error(request, "No course found!")
                    return redirect('teacher:teacher-add-question')

                for idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                    # skip header
                    if idx == 1:
                        continue

                    # skip empty rows
                    if not row:
                        continue

                    # ensure row has 9 columns
                    row = list(row) + [None] * (9 - len(row))

                    exam_name = str(row[0]).strip() if row[0] else ""
                    question_text = str(row[1]).strip() if row[1] else ""

                    option1 = str(row[2] or "")
                    option2 = str(row[3] or "")
                    option3 = str(row[4] or "")
                    option4 = str(row[5] or "")

                    answer = str(row[6] or "")
                    marks = row[7]
                    explanation = str(row[8] or "")

                    if not exam_name or not question_text:
                        continue

                    # Find exam by name (case-insensitive) for this admin
                    exam = Exam.objects.filter(
    admin=admin,
    teacher=teacher,
    exam_name__iexact=exam_name
).first()

                    if not exam:
                        messages.error(request, f"Exam '{exam_name}' not found!")
                        return redirect('teacher:teacher-add-question')

                    # ensure one exam per upload file
                    if target_exam is None:
                        target_exam = exam
                        target_exam_name = exam.exam_name
                    elif exam.id != target_exam.id:
                        messages.error(
                            request,
                            "Excel file contains more than one exam name. Upload one exam at a time."
                        )
                        return redirect('teacher:teacher-add-question')

                    # safe marks
                    try:
                        marks = int(marks)
                    except (TypeError, ValueError):
                        marks = 0

                    # duplicate check
                    if Question.objects.filter(
                        exam=exam,
                        question__iexact=question_text,
                        admin=admin
                    ).exists():
                        continue

                    # save question
                    Question.objects.create(
                        exam=exam,
                        admin=admin,
                        question=question_text,
                        option1=option1,
                        option2=option2,
                        option3=option3,
                        option4=option4,
                        answer=answer,
                        explanation=explanation,
                        marks=marks,
                    )

                    added_count += 1

                if not target_exam:
                    messages.warning(request, "No valid exam found in Excel!")

                else:
                    actual_questions, actual_marks, missing_questions, missing_marks = get_exam_progress(target_exam)

                    if missing_questions > 0 or missing_marks > 0:
                        messages.warning(
                            request,
                            f"⚠ Uploaded {added_count} questions. "
                            f"Missing: {missing_questions} questions and {missing_marks} marks."
                        )
                    else:
                        messages.success(
                            request,
                            f"✅ All questions uploaded successfully! ({added_count} added)"
                        )

            except Exception as e:
                messages.error(request, f"Error: {e}")

            return redirect('teacher:teacher-add-question')

        # ================= MANUAL FORM =================
        elif request.POST.get("manual_submit"):
            form = QuestionForm(request.POST)
            form.fields['exam'].queryset = Exam.objects.filter(
    admin=admin,
    teacher=teacher
)

            if form.is_valid():
                question = form.save(commit=False)

                if question.exam.admin_id != admin.id or question.exam.teacher_id != teacher.id:
                  messages.error(request, "Invalid exam!")
                  return redirect('teacher:teacher-add-question')

                question.admin = admin
                question.save()

                # compare current DB status against expected exam totals
                actual_questions, actual_marks, missing_questions, missing_marks = get_exam_progress(question.exam)

                if missing_questions > 0 or missing_marks > 0:
                    messages.warning(
                        request,
                        f"Question added. Missing: {missing_questions} questions and {missing_marks} marks."
                    )
                else:
                    messages.success(request, "Question added and exam is complete.")

                return redirect('teacher:teacher-add-question')

            else:
                messages.error(request, "Form failed!")

    return render(request, "teacher/teacher_add_question.html", {
        "questionForm": form
    })
@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_publish_exam(request, pk):

    exam = get_object_or_404(Exam, id=pk, teacher=request.user.teacher)

    actual_questions = Question.objects.filter(exam=exam).count()
    actual_marks = Question.objects.filter(exam=exam).aggregate(
        total=Sum('marks')
    )['total'] or 0

    missing_questions = exam.total_questions - actual_questions
    missing_marks = exam.total_marks - actual_marks

    if missing_questions > 0 or missing_marks > 0:
        messages.error(
            request,
            f"❌ Cannot publish! Missing {missing_questions} questions and {missing_marks} marks."
        )
        return redirect('teacher:teacher-view-exam')

    exam.status = "Approved"
    exam.save()

    messages.success(request, "✅ Exam published successfully!")
    return redirect('teacher:teacher-view-exam')

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_view_question_view(request):
    teacher = Teacher.objects.get(user=request.user)

    courses = Course.objects.filter(
        admin=teacher.admin,
        exam__teacher=teacher
    ).distinct().annotate(
        question_number=Count('exam__question', filter=Q(exam__teacher=teacher)),
        total_marks=Sum('exam__question__marks', filter=Q(exam__teacher=teacher))
    )

    return render(request, 'teacher/teacher_view_question.html', {
        'courses': courses
    })
@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def see_question_view(request, pk):

    teacher = request.user.teacher

    course = get_object_or_404(
        QMODEL.Course,
        id=pk,
        admin=teacher.admin
    )

    exams = QMODEL.Exam.objects.filter(
        course=course,
        teacher=teacher   # 🔥 FIX
    )

    questions = Question.objects.filter(exam__in=exams)

    return render(request, 'teacher/see_question.html', {
        'questions': questions
    })
@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_view_question_detail_view(request, pk):
    question = get_object_or_404(
    QMODEL.Question,
    id=pk,
    exam__teacher=request.user.teacher
)
    return render(request, 'teacher/teacher_view_question_detail.html', {'question': question})

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_edit_question_view(request, pk):
    question = get_object_or_404(
    QMODEL.Question,
    id=pk,
    exam__teacher=request.user.teacher
)
    if request.method == 'POST':
        questionForm = QFORM.QuestionForm(request.POST, instance=question)
        if questionForm.is_valid():
            questionForm.save()
            # Redirect to the 'see-question' page for the exam this question belongs to
            return redirect('teacher:see-question', pk=question.exam.course.id)
    else:
        questionForm = QFORM.QuestionForm(instance=question)
    return render(request, 'teacher/teacher_edit_question.html', {'questionForm': questionForm, 'question': question})
@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def remove_question_view(request, pk):

    question = get_object_or_404(
    QMODEL.Question,
    id=pk,
    exam__teacher=request.user.teacher
)
    question.delete()

    return redirect('teacher:teacher-view-question')


# --------------------------------------------------
# Student Management
# --------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_student_view(request):

    admin = get_admin(request)

    context = {
        'total_student': SMODEL.Student.objects.filter(
            admin=admin,
            is_approved=True   # ✅ only approved
        ).count()
    }

    return render(request, 'exam/admin_student.html', context)


@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_view_student_view(request):
    admin = get_admin(request)
    students = SMODEL.Student.objects.filter(admin=admin, is_approved=True)

    return render(request, 'teacher/teacher_view_student.html', {'students': students})

# --------------------------------------------------
# Course Management Page
# --------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_manage_course(request):
    teacher = request.user.teacher
    courses = QMODEL.Course.objects.filter(admin=teacher.admin)

    return render(request, 'teacher/teacher_manage_course.html', {
        'courses': courses
    })

# @login_required(login_url='login')
# @user_passes_test(is_teacher, login_url='login')
# def delete_course_view(request, pk):
#     course = get_object_or_404(QMODEL.Course, id=pk)
#     course.delete()
#     messages.success(request, "Course deleted successfully 🗑️")
#     return redirect('teacher:teacher-manage-course')
# --------------------------------------------------
# Question Management Page
# --------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_manage_question_view(request):
    teacher = request.user.teacher

    courses = QMODEL.Course.objects.filter(
        admin=teacher.admin,
        exam__teacher=teacher
    ).distinct()

    return render(request, 'teacher/teacher_manage_question.html', {
        'courses': courses
    })


# --------------------------------------------------
# Notifications
# --------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_notifications_view(request):

    return render(request, 'teacher/teacher_notifications.html')


# --------------------------------------------------
# Settings
# --------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_doubts_view(request):
    teacher = request.user.teacher
    doubts = SMODEL.Doubt.objects.filter(
    student__admin=teacher.admin
).order_by('-created_at')
    return render(request, 'teacher/teacher_doubts.html', {'doubts': doubts})

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_resolve_doubt_view(request, pk):
    doubt = get_object_or_404(SMODEL.Doubt, id=pk)
    if request.method == 'POST':
        reply = request.POST.get('reply')
        doubt.reply = reply
        doubt.is_resolved = True
        doubt.save()
        messages.success(request, f"Resolution committed for Inquiry TRK-{doubt.id}.")
        return redirect('teacher:teacher-doubts')
    return render(request, 'teacher/teacher_resolve_doubt.html', {'doubt': doubt})

@login_required(login_url='login')
@user_passes_test(is_teacher, login_url='login')
def teacher_settings_view(request):

    user = request.user
    teacher = request.user.teacher

    if request.method == 'POST':

        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        # ✅ profile pic (optional)
        if request.FILES.get('profile_pic'):
            teacher.profile_pic = request.FILES.get('profile_pic')
            teacher.save()

        # password
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 and password1 == password2:
            user.set_password(password1)
            update_session_auth_hash(request, user)

        user.save()

        messages.success(request, "Profile updated successfully ✅")

        return redirect('teacher:teacher-settings')

    return render(request, 'teacher/teacher_settings.html')