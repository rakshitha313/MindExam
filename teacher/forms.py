from django import forms
from django.contrib.auth.models import User
from .models import Teacher
from exam.models import Course
from exam.models import Question
from .models import Teacher, Institution
from exam.models import Admin   # 

class TeacherUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']


class TeacherForm(forms.ModelForm):
    # USED FOR SIGNUP (with admin dropdown)
    admin = forms.ModelChoiceField(
        queryset=Admin.objects.all(),
        empty_label="Select Institution",
        required=True
    )

    class Meta:
        model = Teacher
        fields = ['address', 'mobile', 'profile_pic', 'admin']


class TeacherAdminForm(forms.ModelForm):
    # USED FOR ADMIN PANEL (NO admin field)

    class Meta:
        model = Teacher
        fields = ['address', 'mobile', 'profile_pic']

class TeacherSalaryForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['salary']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ['admin']   # 🔥 FIX


class UploadExcelForm(forms.Form):
    file = forms.FileField(label="Select Excel File")