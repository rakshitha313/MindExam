from django import forms
from django.contrib.auth.models import User
from .models import Student
from exam.models import Admin, Course, Branch


class StudentUserForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput())
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password or confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data


class StudentForm(forms.ModelForm):
    admin = forms.ModelChoiceField(
        queryset=Admin.objects.all(),
        required=False,
        empty_label="Select Institution"
    )

    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        empty_label="Select Branch"
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label="Select Course"
    )

    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = Student
        fields = ['admin', 'branch', 'course', 'usn', 'profile_pic', 'address', 'mobile']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in ['admin', 'branch', 'course', 'usn', 'profile_pic', 'address', 'mobile']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        self.fields['branch'].queryset = Branch.objects.all()
        self.fields['course'].queryset = Course.objects.all()

        if 'admin' in self.data and self.data.get('admin'):
            try:
                admin_id = int(self.data.get('admin'))
                self.fields['branch'].queryset = Branch.objects.filter(
                    course__admin_id=admin_id
                ).distinct()
                self.fields['course'].queryset = Course.objects.filter(
                    admin_id=admin_id
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.admin:
            self.fields['branch'].queryset = Branch.objects.filter(
                course__admin=self.instance.admin
            ).distinct()
            self.fields['course'].queryset = Course.objects.filter(
                admin=self.instance.admin
            )

        if 'branch' in self.data and self.data.get('branch'):
            try:
                branch_id = int(self.data.get('branch'))
                self.fields['course'].queryset = self.fields['course'].queryset.filter(
                    branch_id=branch_id
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.branch:
            self.fields['course'].queryset = self.fields['course'].queryset.filter(
                branch=self.instance.branch
            )

    def clean_usn(self):
        usn = self.cleaned_data.get('usn')
        if usn and Student.objects.filter(usn=usn).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("USN already exists")
        return usn

    def clean(self):
        cleaned_data = super().clean()
        admin = cleaned_data.get('admin')
        branch = cleaned_data.get('branch')
        course = cleaned_data.get('course')

        if course and admin and course.admin != admin:
            self.add_error('course', "Selected course does not belong to this institution.")

        if course and branch and course.branch != branch:
            self.add_error('course', "Selected course does not belong to this branch.")

        return cleaned_data