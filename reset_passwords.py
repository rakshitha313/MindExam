from django.contrib.auth.models import User, Group

# 1. Reset Admin password
try:
    admin_user = User.objects.get(username='admin12')
    admin_user.set_password('admin123')
    admin_user.save()
    print("Admin password reset: admin12 / admin123")
except User.DoesNotExist:
    pass

# 2. Reset Student password
try:
    student1 = User.objects.get(username='apsis')
    student1.set_password('student123')
    student1.save()
    print("Student password reset: apsis / student123")
except User.DoesNotExist:
    pass

# 3. Create a Teacher if none exists
teacher_group, _ = Group.objects.get_or_create(name='TEACHER')
teacher_user, created = User.objects.get_or_create(username='teacher1')
teacher_user.set_password('teacher123')
teacher_user.save()
teacher_user.groups.add(teacher_group)

if created:
    print("New teacher created: teacher1 / teacher123")
else:
    print("Teacher password reset: teacher1 / teacher123")
