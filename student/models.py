
# student/models.py
from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey('exam.Course', on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey('exam.Branch', on_delete=models.CASCADE, null=True, blank=True)
    usn = models.CharField(max_length=50, unique=True, null=True, blank=True)
    admin = models.ForeignKey('exam.Admin', on_delete=models.CASCADE)

    # ✅ NEW FIELDS
    
    is_approved = models.BooleanField(default=False)
    
    is_rejected = models.BooleanField(default=False)

    profile_pic = models.ImageField(upload_to='profile_pic/', null=True, blank=True)
    address = models.CharField(max_length=250)
    mobile = models.CharField(max_length=20)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name
# Notification Model
# ------------------------
class Notification(models.Model):
    
    student = models.ForeignKey(Student,on_delete=models.CASCADE)

    message = models.CharField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

# ------------------------
# Certificate Model
# ------------------------
class Certificate(models.Model):

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    course = models.ForeignKey('exam.Course', on_delete=models.CASCADE)
    certificate_file = models.FileField(upload_to='certificates/')

    issued_date = models.DateTimeField(auto_now_add=True)


# ------------------------
# Message Model
# ------------------------
class Message(models.Model):

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    message = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
class Doubt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey('exam.Course', on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    reply = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doubt by {self.student.user.username}"
# models.py

class StudentAnswer(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    exam = models.ForeignKey('exam.Exam', on_delete=models.CASCADE)
    question = models.ForeignKey('exam.Question', on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=10)