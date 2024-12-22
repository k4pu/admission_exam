from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello this is admission exam db app!")

def login(request):
    context = {}
    return render(request, "admission_exam_db/login.html", context)

def students(request):
    context ={}
    return render(request, "admission_exam_db/students.html", context)

def student_detail(request, student_id):
    context ={
        "student_id": student_id,
    }
    return render(request, "admission_exam_db/student_detail.html", context)
