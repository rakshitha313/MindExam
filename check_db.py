import os
import sys
import django

# Add project directory to sys.path
sys.path.append(r'C:\Users\Laxmi\.gemini\antigravity\playground\blazing-andromeda\Mindexam\Mindexamonline')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlinexam.settings')
django.setup()

from exam.models import Exam, Result
from student.models import Student

def check_exams():
    print("--- Students ---")
    for s in Student.objects.all():
        print(f"ID: {s.id}, User: {s.user.username}, Name: {s.user.first_name}")

    print("\n--- Exams ---")
    exams = Exam.objects.all()
    if not exams.exists():
        print("No exams found.")
    for e in exams:
        print(f"ID: {e.id}, Name: {e.exam_name}, Status: {e.status}")

    print("\n--- Results ---")
    for r in Result.objects.all():
        print(f"Student: {r.student.user.username}, Exam: {r.exam.exam_name}, Marks: {r.marks}")

if __name__ == "__main__":
    check_exams()
