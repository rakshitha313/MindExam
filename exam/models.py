from django.db import models

from django.contrib.auth.models import User
import uuid
from django.db import models
from django.apps import apps
# ============================
# CATEGORY & DIFFICULTY CHOICES
# ============================

CATEGORY_CHOICES = (
    ('IT Skills', 'IT Skills'),
    ('Aptitude', 'Aptitude'),
    ('Academic', 'Academic'),
    ('Skill Assessment', 'Skill Assessment'),
)

DIFFICULTY_CHOICES = (
    ('Easy','Easy'),
    ('Medium','Medium'),
    ('Hard','Hard'),
)

ANSWER_CHOICES = (
    ('option1', 'Option 1'),
    ('option2', 'Option 2'),
    ('option3', 'Option 3'),
    ('option4', 'Option 4'),
)

# ============================
# Admin Model
# ============================

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="My Admin")  # default for new + existing rows
    institution_name = models.CharField(max_length=200, default="My Institution")
    profile_pic = models.ImageField(upload_to='profile/', null=True, blank=True)

    def __str__(self):
        return self.institution_name

# ============================
# Course Model
# ============================
class Branch(models.Model):
    
    name = models.CharField(max_length=100)
       # 👈 add this

    def __str__(self):
        return self.name
class Course(models.Model):
    course_name = models.CharField(max_length=50)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True) 
    admin = models.ForeignKey(Admin, on_delete=models.PROTECT)

    course_code = models.CharField(max_length=20, unique=True, null=True, blank=True)

    exam_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    start_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.exam_code:
            self.exam_code = str(uuid.uuid4())[:10].upper()

        if not self.course_code:
            self.course_code = self.exam_code[:6]  # auto fallback

        super().save(*args, **kwargs)

    def __str__(self):
        return self.course_name

# ============================
# Exam Model
# ============================

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.PROTECT)
    exam_name = models.CharField(max_length=100, default='New Exam')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    total_questions = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    pass_marks = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=30)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    instructions = models.TextField(blank=True, null=True)
    exam_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    teacher = models.ForeignKey('teacher.Teacher', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.course.course_name} ({self.status})"

# ============================
# Question Model
# ============================

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.PROTECT)
    question = models.CharField(max_length=500)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    answer = models.CharField(max_length=20)  # option1 / option2 / option3 / option4
    explanation = models.TextField(blank=True, null=True)
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.exam.course.course_name}: {self.question[:50]}"

# ============================
# Result Model
# ============================

class Result(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.PROTECT)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student} - {self.exam}"

    @property
    def percentage(self):
        if self.exam.total_marks > 0:
            return round((self.marks / self.exam.total_marks) * 100, 1)
        return 0
