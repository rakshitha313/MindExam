from django.contrib import admin
from .models import Course, Question, Result, Exam
from student.models import Notification, Student
from django.contrib import admin
from .models import Admin
from .models import Branch
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks', 'date')


class ExamAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)

        students = Student.objects.all()

        for student in students:
            Notification.objects.create(
                student=student,
                message=f"New Exam Available: {obj.course.course_name}. Exam Code: {obj.exam_code}"
            )
admin.site.register(Admin)

admin.site.register(Result, ResultAdmin)
admin.site.register(Course)
admin.site.register(Question)
admin.site.register(Branch)
admin.site.register(Exam, ExamAdmin)