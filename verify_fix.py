import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlinexam.settings')
django.setup()

from exam.models import Exam, Result, Course
from student.models import Student
from django.contrib.auth.models import User
from django.test import RequestFactory
from student.views import check_marks_view
from django.shortcuts import get_object_or_404

def verify():
    print("--- Starting Verification ---")
    
    # 1. Create a test user and student
    user, created = User.objects.get_or_create(username='test_student_fix')
    if created:
        user.set_password('password123')
        user.save()
    
    student, _ = Student.objects.get_or_create(user=user)
    
    # 2. Create a test course and exam
    course, _ = Course.objects.get_or_create(course_name='Test Course Fix', defaults={'question_number': 5, 'total_marks': 50})
    exam, _ = Exam.objects.get_or_create(course=course, exam_name='Test Exam Fix', defaults={'total_questions': 5, 'total_marks': 50, 'duration': 30, 'status': 'Approved'})
    
    # 3. Create a result
    result, _ = Result.objects.get_or_create(student=student, exam=exam, defaults={'marks': 45})
    
    print(f"Created/Found Exam ID: {exam.id}")
    print(f"Created/Found Result ID: {result.id}")
    
    # 4. Simulate a request to check_marks_view with the EXAM ID
    factory = RequestFactory()
    request = factory.get(f'/student/check-marks/{exam.id}/')
    request.user = user
    
    print(f"Testing check_marks_view with PK (Exam ID) = {exam.id}")
    
    try:
        response = check_marks_view(request, pk=exam.id)
        if response.status_code == 200:
            print("SUCCESS: check_marks_view returned 200 OK with Exam ID.")
        else:
            print(f"FAILURE: check_marks_view returned status code {response.status_code}")
    except Exception as e:
        print(f"FAILURE: check_marks_view raised an exception: {e}")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify()
