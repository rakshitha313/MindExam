from .models import Teacher

def get_admin(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        print("TEACHER:", teacher)
        print("ADMIN FROM UTILITY:", teacher.admin)   # 👈 DEBUG
        return teacher.admin
    except Teacher.DoesNotExist:
        print("NO TEACHER FOUND")
        return None