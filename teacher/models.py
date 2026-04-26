from django.db import models
from django.contrib.auth.models import User

class Institution(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name
class Teacher(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    course = models.ForeignKey('exam.Course', on_delete=models.CASCADE, null=True, blank=True)
    admin = models.ForeignKey('exam.Admin', on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile/', blank=True, null=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    status= models.BooleanField(default=False)
    salary=models.PositiveIntegerField(null=True)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"