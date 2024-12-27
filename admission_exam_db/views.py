from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .forms import UniversityFacultyCSVUploadForm

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

def upload_university_faculty(request):
    if request.method == "POST":
        form = UniversityFacultyCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
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
                universit.objects.update_or_create(
                    university_faculty_code=university_faculty_code,
                    defaults={
                        'university_name': university_name,
                        'uiversity_faculty_code': uiversity_faculty_code,
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
