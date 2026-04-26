# exam/forms.py
from django.contrib.auth.models import User
from django import forms
from . import models
from student.models import Student
from exam.models import Exam
from .models import Course
# -------------------------------
# Contact Form
# -------------------------------
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30, label="Name")
    Email = forms.EmailField(label="Email")
    Message = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}),
        label="Message"
    )

# -------------------------------
# Teacher Salary Form
# -------------------------------
class TeacherSalaryForm(forms.Form):
    salary = forms.IntegerField(label="Salary")

class TeacherUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }    
# -------------------------------
# Branch Form
# -------------------------------
class BranchForm(forms.ModelForm):
    class Meta:
        model = models.Branch
        fields = ['name']
        labels = {
            'name': 'Branch Name'
        }

# -------------------------------
# Course Form
# -------------------------------
class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = ['course_name', 'exam_code', 'branch']
        labels = {
            'course_name': "Course Name",
            'exam_code': "Course Code",
            'branch': "Branch"
        }

    def __init__(self, *args, **kwargs):
        admin = kwargs.pop('admin', None)
        super().__init__(*args, **kwargs)

        if admin:
            self.fields['branch'].queryset = models.Branch.objects.all()
# -------------------------------
# Question Form
# -------------------------------
class QuestionForm(forms.ModelForm):
    
    exam = forms.ModelChoiceField(
        queryset=models.Exam.objects.all(),
        empty_label="Select Exam"
    )

    # ✅ ADD THIS
    ANSWER_CHOICES = [
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
        ('option4', 'Option 4'),
    ]

    answer = forms.ChoiceField(
        choices=ANSWER_CHOICES,
        widget=forms.Select(attrs={'class': 'premium-input'})
    )

    class Meta:
        model = models.Question
        fields = [
            'exam',
            'question',
            'marks',
            'option1',
            'option2',
            'option3',
            'option4',
            'answer',
            'explanation'
        ]
# -------------------------------
# Exam Form
# -------------------------------
class ExamForm(forms.ModelForm):
    
    class Meta:
        model = models.Exam

        fields = [
            'course',
            'exam_name',
            'category',
            'total_questions',   # ✅ ADD THIS
            'total_marks', 
            'pass_marks',
            'duration',
            'start_time',
            'end_time',
            'instructions'
        ]

        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'glass-input'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'glass-input'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        admin = kwargs.pop('admin', None)
        super().__init__(*args, **kwargs)

        print("FORM ADMIN:", admin)

        if admin:
            self.fields['course'].queryset = models.Course.objects.filter(admin=admin)

        # safe datetime formats
        self.fields['start_time'].input_formats = [
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d-%m-%Y %H:%M',
            '%m/%d/%Y %H:%M',
        ]

        self.fields['end_time'].input_formats = self.fields['start_time'].input_formats
# -------------------------------
# Optional Result Form (if needed)
# -------------------------------
class ResultForm(forms.ModelForm):
    class Meta:
        model = models.Result
        fields = ['student', 'exam', 'marks']
        labels = {
            'student': "Student",
            'exam': "Exam",
            'marks': "Marks Obtained"
        }

# -------------------------------
# Admin User Form
# -------------------------------
class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    institution_name = forms.CharField(max_length=200)

    class Meta:
        model = User
        fields = ['username', 'password', 'institution_name']
        