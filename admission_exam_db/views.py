from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .forms import UniversityFacultyCSVUploadForm, StudentCSVUploadForm, UserCSVUploadForm, StudentAdmissionExamForm

from .models import Student, UniversityFaculty, StudentAdmissionExam
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.db.models import Q

import csv

def is_admin(user):
    return user.is_superuser

@login_required
def index(request):
    context = {}
    return render(request, "admission_exam_db/index.html", context)

@login_required
def student(request):
    student_list = Student.objects.order_by("student_id")
    context ={
        'nbar': 'student',
        'student_list': student_list,
    }
    return render(request, "admission_exam_db/student.html", context)

@login_required
def admission_exam(request):
    admission_exam_list = StudentAdmissionExam.objects.order_by("id")
    context ={
        'nbar': 'admission_exam',
        'admission_exam_list': admission_exam_list,
    }
    return render(request, "admission_exam_db/admission_exam.html", context)

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    student_admission_exam_list = StudentAdmissionExam.objects.filter(student=student)
    context ={
        'nbar': 'student_detail',
        'student_id': student_id,
        'student_name': ' '.join([student.family_name, student.given_name]),
        'student_admission_exam_list': student_admission_exam_list,
    }
    return render(request, "admission_exam_db/student_detail.html", context)

@login_required
@user_passes_test(is_admin)
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
            return redirect('admission_exam_db:upload_success') # アップロード成功画面にリダイレクト
    else:
        form = UniversityFacultyCSVUploadForm()
    context = {
        'nbar': 'upload_university_faculty',
        'form': form,
    }
    return render(request, 'admission_exam_db/upload_university_faculty.html', context)

@login_required
@user_passes_test(is_admin)
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
            return redirect('admission_exam_db:upload_success') # アップロード成功画面にリダイレクト
    else:
        form = StudentCSVUploadForm()
    context = {
        'nbar': 'upload_student',
        'form': form,
    }
    return render(request, 'admission_exam_db/upload_student.html', context)

@login_required
@user_passes_test(is_admin)
def upload_user(request):
    if request.method == "POST":
        form = UserCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            try:
                decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                reader = csv.DictReader(decoded_file)

                success_count = 0
                error_count = 0

                for row in reader:
                    try:
                        username = row['username']
                        password = row['password']
                        email = row['email']

                        # データモデルに保存
                        user, created = User.objects.update_or_create(
                            username=username,
                            defaults={
                                'email': email,
                            }
                        )
                        if created or not user.check_password(password):# 新規作成またはパスワードが変更された場合
                            user.set_password(password)
                            user.save()

                        success_count += 1
                    except KeyError as e:
                        # 必須フィールドが不足している場合
                        error_count += 1
                        messages.error(request, f"CSVに必須フィールドが不足しています： {e}")
                    except Exception as e:
                        # その他のエラー
                        error_count += 1
                        messages.error(request, f"エラーが発生しました： {e}")

                messages.success(request, f"アップロード完了： {success_count}件成功, {error_count}件失敗")
                return redirect('admission_exam_db:upload_success') # アップロード成功画面にリダイレクト
            except UnicodeDecodeError:
                messages.error(request, "ファイルのエンコーディングエラーです。UTF-8で保存されたCSVを使用してください。")
    else:
        form = UserCSVUploadForm()
    context = {
        'nbar': 'upload_user',
        'form': form,
    }
    return render(request, 'admission_exam_db/upload_user.html', context)

def upload_success(request):
    context = {}
    return render(request, 'admission_exam_db/upload_success.html', context)

@login_required
def create_student_admission_exam(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        form = StudentAdmissionExamForm(request.POST, student=student)# 生徒はすでに指定しているので、formで新たに入力する手間を省くためにstudentオブジェクトを渡す
        if form.is_valid():
            form.save()
            return redirect('admission_exam_db:student_detail', student_id=student_id)
    else:
        form = StudentAdmissionExamForm(student=student)# studentオブジェクトを渡す

    context ={
        'nbar': 'student',
        'form': form,
        'student_id': student_id,
        'student_name': ' '.join([student.family_name, student.given_name]),
    }
    return render(request, 'admission_exam_db/student_admission_exam_form.html', context)

@login_required
def edit_student_admission_exam(request, student_id, student_admission_exam_id):
    student = get_object_or_404(Student, student_id=student_id)
    admission_exam = get_object_or_404(StudentAdmissionExam, id=student_admission_exam_id, student=student)

    if request.method == 'POST':
        form = StudentAdmissionExamForm(request.POST, instance=admission_exam)
        if form.is_valid():
            form.save()
            return redirect('admission_exam_db:student_detail', student_id=student_id)

    else:
        form = StudentAdmissionExamForm(instance=admission_exam)

    context = {
        'nbar': 'student',
        'form': form,
        'student_id': student_id,
        'student_admission_exam_id': student_admission_exam_id,
        'student_name': ' '.join([student.family_name, student.given_name]),
    }
    return render(request, 'admission_exam_db/student_admission_exam_form.html', context)

def delete_student_admission_exam(request, student_id, student_admission_exam_id):
    student = get_object_or_404(Student, student_id=student_id)
    admission_exam = get_object_or_404(StudentAdmissionExam, id=student_admission_exam_id, student=student)

    # 削除処理
    admission_exam.delete()
    messages.success(request, "受験データ削除に成功しました")

    return redirect('admission_exam_db:student_detail', student_id=student_id)


@login_required
def university_faculty_autocomplete(request):
    query = request.GET.get('q', '') # クエリパラメータ 'q' を取得
    if query:
        faculties = UniversityFaculty.objects.filter(
            Q(display_name__startswith=query) | Q(university_faculty_code__startswith=query)
        )[:50] # 先頭一致
    else:
        faculties = UniversityFaculty.objects.none()
    results = [{"id": faculty.university_faculty_code, "name": faculty.display_name} for faculty in faculties]
    return JsonResponse(results, safe=False)

def user(request):
    context = {}
    return render(request, 'admission_exam_db/user.html', context)
