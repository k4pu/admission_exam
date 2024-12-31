from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .forms import UniversityFacultyCSVUploadForm, StudentCSVUploadForm

from.models import Student, UniversityFaculty

import csv

def index(request):
    return HttpResponse("Hello this is admission exam db app!")

def login(request):
    context = {}
    return render(request, "admission_exam_db/login.html", context)

def students(request):
    student_list = Student.objects.order_by("student_id")
    context ={
        "student_list": student_list,
    }
    return render(request, "admission_exam_db/students.html", context)

def student_detail(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    context ={
        "student_id": student_id,
        "student_name": " ".join([student.family_name, student.given_name])
    }
    return render(request, "admission_exam_db/student_detail.html", context)

def upload_university_faculty(request):
    if request.method == "POST":
        form = UniversityFacultyCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                university_faculty_code = row['university_faculty_code']
                university_name = row['university_name']
                faculty_name = row['faculty_name']
                department_name = row['department_name']
                display_name = row['display_name']
                faculty_system_midstream_name = row['faculty_system_midstream_name']
                faculty_system_field_code = row['faculty_system_field_code']
                faculty_system_field_name = row['faculty_system_field_name']

                # データモデルに保存
                UniversityFaculty.objects.update_or_create(
                    university_faculty_code=university_faculty_code,
                    defaults={
                        'university_name': university_name,
                        'university_faculty_code': university_faculty_code,
                        'university_name': university_name,
                        'faculty_name': faculty_name,
                        'department_name': department_name,
                        'display_name': display_name,
                        'faculty_system_midstream_name': faculty_system_midstream_name,
                        'faculty_system_field_code': faculty_system_field_code,
                        'faculty_system_field_name': faculty_system_field_name,
                    }
                )
            return redirect('admission_exam_db/upload_university_faculty_success.html') # アップロード成功画面にリダイレクト
    else:
        form = UniversityFacultyCSVUploadForm()
    return render(request, 'admission_exam_db/upload_university_faculty.html', {'form': form})

def upload_student(request):
    if request.method == "POST":
        form = StudentCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                student_id = row['student_id']
                homeroom_class = row['homeroom_class']
                attendance_number = row['attendance_number']
                family_name = row['family_name']
                given_name = row['given_name']
                family_name_kana = row['family_name_kana']
                given_name_kana = row['given_name_kana']

                # データモデルに保存
                Student.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        'homeroom_class': homeroom_class,
                        'attendance_number': attendance_number,
                        'family_name': family_name,
                        'given_name': given_name,
                        'family_name_kana': family_name_kana,
                        'given_name': given_name,
                        'given_name_kana': given_name_kana,
                    }
                )
            return redirect('admission_exam_db/upload_student.html') # アップロード成功画面にリダイレクト
    else:
        form = StudentCSVUploadForm()
    return render(request, 'admission_exam_db/upload_student.html', {'form': form})
