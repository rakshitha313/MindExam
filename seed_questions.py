import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlinexam.settings')
django.setup()

from exam.models import Exam, Question

def seed_exam(exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
        questions = [
            ("What is the output of print(2 ** 3)?", "6", "8", "9", "12", "option2"),
            ("Which keyword creates a function?", "func", "define", "def", "lambda", "option3"),
            ("Correct way to create a list?", "(1,2)", "{1,2}", "[1,2]", "list(1,2)", "option3"),
            ("How to start a comment?", "//", "/*", "#", "--", "option3"),
            ("Not a numeric type?", "int", "float", "complex", "double", "option4"),
            ("What does len() do?", "Sum", "Length", "String", "Delete", "option2"),
            ("Add element to end of list?", "add()", "insert()", "append()", "push()", "option3"),
            ("Default return of function?", "0", "None", "False", "Error", "option2"),
            ("Floor division operator?", "/", "//", "%", "**", "option2"),
            ("Create a dictionary?", "[]", "()", "{}", "<>", "option3"),
        ]
        
        # Clear existing for this exam to avoid duplicates if re-run
        Question.objects.filter(exam=exam).delete()
        
        for text, o1, o2, o3, o4, ans in questions:
            Question.objects.create(
                exam=exam,
                question=text,
                option1=o1,
                option2=o2,
                option3=o3,
                option4=o4,
                answer=ans,
                marks=1
            )
        print(f"Seeded 10 questions for Exam: {exam.exam_name}")
    except Exam.DoesNotExist:
        print(f"Exam with ID {exam_id} not found.")

if __name__ == "__main__":
    seed_exam(1)
    seed_exam(2)
