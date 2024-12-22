from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from.models import Student

def index(request):
    return HttpResponse("Hello this is admission exam db app!")

def login(request):
    context = {}
    return render(request, "admission_exam_db/login.html", context)

def students(request):
    context ={}
    return render(request, "admission_exam_db/students.html", context)

def student_detail(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    context ={
        "student_id": student_id,
        "student_name": " ".join([student.family_name, student.given_name])
    }
    return render(request, "admission_exam_db/student_detail.html", context)
