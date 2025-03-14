from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from .forms import UniversityFacultyCSVUploadForm, StudentCSVUploadForm, UserCSVUploadForm, StudentAdmissionExamForm, StudentAdmissionExamCSVUploadForm

from .models import Student, UniversityFaculty, StudentAdmissionExam
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.db.models import Q, Count

import csv
import io
import logging
import datetime

logger = logging.getLogger('django')


def is_admin(user):
    return user.is_superuser

def is_editor(user):
    if user.groups.filter(name="editor").exists() or user.is_superuser:
        return True
    else:
        return False

@login_required
def index(request):
    context = {
        'nbar': 'home',
    }
    return render(request, "admission_exam_db/index.html", context)

@login_required
def student(request):
    student_list = Student.objects.order_by("-graduation_year", "homeroom_class", "attendance_number")
    context ={
        'nbar': 'student',
        'student_list': student_list,
    }
    return render(request, "admission_exam_db/student.html", context)

@login_required
def admission_exam(request):
    admission_exam_list = StudentAdmissionExam.objects.order_by("-year_to_take", "university_faculty_id")
    passed_choices = [ {"key":key, "value":value} for key, value in StudentAdmissionExam.PASSED_CHOICES ]
    rejected_choices = [ {"key":key, "value":value} for key, value in StudentAdmissionExam.REJECTED_CHOICES ]
    yet_choices = [ {"key":key, "value":value} for key, value in StudentAdmissionExam.YET_CHOICES ]
    context ={
        'nbar': 'admission_exam',
        'admission_exam_list': admission_exam_list,
        'passed_choices': passed_choices,
        'rejected_choices': rejected_choices,
        'yet_choices': yet_choices,
    }
    return render(request, "admission_exam_db/admission_exam.html", context)

@login_required
def passed_exam_count(request):
    # 今年の取得
    dt = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    exam_year = dt.year
    university_faculty_list = UniversityFaculty.objects.annotate(passed_exam_count=Count("studentadmissionexam", filter=Q(studentadmissionexam__result_status="P"))).filter(passed_exam_count__gt=0).filter(studentadmissionexam__year_to_take=exam_year)# １対多の多側は小文字らしい
    university_name_list = university_faculty_list.values("university_name").order_by("university_faculty_code")

    university_list = {
        university_name['university_name']: {}
        for university_name in university_name_list
    }

    for faculty in university_faculty_list:
        university_list[faculty.university_name][faculty.faculty_name] = faculty.passed_exam_count

    context ={
        'university_list': university_list,
    }
    return render(request, "admission_exam_db/passed_exam_count.html", context)


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    prev_student = Student.objects.filter(
        Q(homeroom_class__lt=student.homeroom_class) |
        Q(homeroom_class=student.homeroom_class, attendance_number__lt=student.attendance_number)
    ).order_by('-homeroom_class', '-attendance_number').first()

    next_student = Student.objects.filter(
        Q(homeroom_class__gt=student.homeroom_class) |
        Q(homeroom_class=student.homeroom_class, attendance_number__gt=student.attendance_number)
    ).order_by('homeroom_class', 'attendance_number').first()

    student_admission_exam_list = StudentAdmissionExam.objects.filter(student=student).order_by("-year_to_take", "university_faculty_id")

    context ={
        'nbar': 'student_detail',
        'student_id': student_id,
        'student_name': ' '.join([student.family_name, student.given_name]),
        'prev_student': prev_student,
        'next_student': next_student,
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
def download_template_csv(request, file_kind):
    filename = f"{file_kind}_template.csv"

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    if file_kind == "university_faculty":
        writer.writerow(["university_faculty_code", "university_name", "faculty_name", "department_name", "display_name", "faculty_system_midstream_name", "faculty_system_field_code", "faculty_system_field_name"])
        writer.writerow(["10001" ,"旭川医科" ,"医" ,"医－前" ,"旭川医科_医_医－前" ,"医・歯・薬・保健" ,"5101" ,"医"])
    elif file_kind == "student":
        writer.writerow(["student_id", "homeroom_class", "attendance_number", "family_name", "given_name", "family_name_kana", "given_name_kana", "graduation_year"])
        writer.writerow(["1900123", "A", "01", "昭和", "秀太", "しょうわ", "しゅうた", "2025"])
    elif file_kind == "user":
        writer.writerow(["username", "password", "email"])
        writer.writerow(["test", "testpass", "test@showa-shuei.ed.jp"])
    elif file_kind == "student_admission_exam":
        writer.writerow(["student_admission_exam_id", "student_id", "university_faculty_code", "year_to_take", "preference", "result"])
        writer.writerow(["30", "1990123", "10001", "2025", "A1", "AE"])

    # UTF-8-SIGにエンコード
    csv_data = output.getvalue().encode("utf-8-sig")
    output.close()

    response = HttpResponse(
        io.BytesIO(csv_data),
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename={filename}'},
    )
    
    return response

class Echo:# https://docs.djangoproject.com/ja/5.1/howto/outputting-csv/よりストリーミングCSVダウンロード用クラス ファイルオブジェクトのかわりに動作して、メモリを消費しない
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value# 受け取った値をそのまま返すのでメモリを消費しない

@login_required
@user_passes_test(is_editor)
def download_data_csv(request, file_kind):
    filename = f"{file_kind}_data.csv"

    if file_kind == "student":
        student_list = Student.objects.order_by("homeroom_class", "attendance_number")

        header_row = [["student_id", "homeroom_class", "attendance_number", "family_name", "given_name", "family_name_kana", "given_name_kana"]]
        data_rows = [[student.student_id, student.homeroom_class, student.attendance_number, student.family_name, student.given_name, student.family_name_kana, student.given_name_kana] for student in student_list]

    elif file_kind == "university_faculty":
        faculty_list = UniversityFaculty.objects.order_by("university_faculty_code")

        header_row = [["university_faculty_code", "university_name", "department_name", "display_name", "faculty_system_midstream_name", "faculty_system_midstream_name", "faculty_system_field_code", "faculty_system_field_code"]]
        data_rows = [[faculty.university_faculty_code, faculty.university_name, faculty.department_name, faculty.display_name, faculty.faculty_system_midstream_name, faculty.faculty_system_midstream_name, faculty.faculty_system_field_code, faculty.faculty_system_field_code] for faculty in faculty_list]

    elif file_kind == "student_admission_exam":
        admission_exam_list = StudentAdmissionExam.objects.order_by("id")# TODO これはより良いorderがありそうなので考える
        header_row = [["student_admission_exam_id", "student_id", "university_faculty_code", "year_to_take", "preference", "result", "result_status"]]
        data_rows = [[exam.id, exam.student.student_id, exam.university_faculty.university_faculty_code, exam.year_to_take, exam.preference, exam.result, exam.result_status] for exam in admission_exam_list]

    elif file_kind == "student_admission_exam_display":
        admission_exam_list = StudentAdmissionExam.objects.order_by("year_to_take", "student__homeroom_class", "student__attendance_number", "university_faculty__university_faculty_code")# TODO これはより良いorderがありそうなので考える
        header_row = [["受験年", "卒業年", "組", "番", "氏名", "大学_学部", "結果詳細", "結果", "備考"]]
        data_rows = [[exam.year_to_take, exam.student.graduation_year, exam.student.homeroom_class, exam.student.attendance_number, exam.student.family_name + " " + exam.student.given_name, exam.university_faculty.display_name, exam.get_result_display(), exam.get_result_status_display(), exam.info] for exam in admission_exam_list]

    elif file_kind == "preference_choice":
        preference_correspondense_list = StudentAdmissionExam.PREFERENCE_CHOICES
        header_row = [["preference", "preference_label"]]
        data_rows = [[code, label] for code, label in preference_correspondense_list]

    elif file_kind == "result_choice":
        result_corespondence_list = StudentAdmissionExam.RESULT_CHOICES
        header_row = [["result", "result_label"]]
        data_rows = [[code, label] for code, label in result_corespondence_list]

    write_rows = header_row + data_rows

    # csvデータを作成
    output =io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerows(write_rows)

    # **UTF-8-SIG にエンコード BOM付きUTF-8
    csv_data = output.getvalue().encode("utf-8-sig")
    output.close()

    # pseudo_buffer = Echo()
    # writer = csv.writer(pseudo_buffer)
    return StreamingHttpResponse(
        # (writer.writerow(row) for row in write_rows),
        io.BytesIO(csv_data),
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename={filename}'},
    )

@login_required
def download_data(request):
    context = {
        'nbar': 'download_data',
    }
    return render(request, "admission_exam_db/download_data.html", context)

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
                graduation_year = row['graduation_year']

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
                        'graduation_year': graduation_year,
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
@user_passes_test(is_admin)
def upload_student_admission_exam(request):
    if request.method == "POST":
        form = StudentAdmissionExamCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                student_admission_exam_id = row.get('student_admission_exam_id', None)# なければNone
                student_id = row['student_id']
                university_faculty_code = row['university_faculty_code']
                year_to_take = row['year_to_take']
                preference = row['preference']
                result = row['result']

                student = get_object_or_404(Student, student_id=student_id)
                university_faculty = get_object_or_404(UniversityFaculty, university_faculty_code=university_faculty_code)
                # データモデルに保存
                if student_admission_exam_id:
                    StudentAdmissionExam.objects.update_or_create(
                        id=student_admission_exam_id,
                        defaults = {
                        'student': student,
                        'university_faculty': university_faculty,
                        'year_to_take': year_to_take,
                        'preference': preference,
                        'result': result,
                        }
                    )
                else:
                    StudentAdmissionExam.objects.create(
                        student=student,
                        university_faculty=university_faculty,
                        year_to_take=year_to_take,
                        preference=preference,
                        result=result,
                    )

            return redirect('admission_exam_db:upload_success') # アップロード成功画面にリダイレクト
    else:
        form = StudentAdmissionExamCSVUploadForm()
    context = {
        'nbar': 'upload_student_admission_exam',
        'form': form,
    }
    return render(request, 'admission_exam_db/upload_student_admission_exam.html', context)

@login_required
@user_passes_test(is_editor)
def create_student_admission_exam(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        form = StudentAdmissionExamForm(request.POST, student=student)# 生徒はすでに指定しているので、formで新たに入力する手間を省くためにstudentオブジェクトを渡す
        if form.is_valid():

            form.save(user=request.user)
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
@user_passes_test(is_editor)
def edit_student_admission_exam(request, student_id, student_admission_exam_id):
    student = get_object_or_404(Student, student_id=student_id)
    admission_exam = get_object_or_404(StudentAdmissionExam, id=student_admission_exam_id, student=student)

    if request.method == 'POST':
        form = StudentAdmissionExamForm(request.POST, instance=admission_exam)
        if form.is_valid():

            form.save(commit=True, user=request.user)
            return redirect('admission_exam_db:student_detail', student_id=student_id)

    else:
        form = StudentAdmissionExamForm(instance=admission_exam)

    context = {
        'nbar': 'student',
        'form': form,
        'student_id': student_id,
        'student_admission_exam_id': student_admission_exam_id,
        'university_faculty_display_name': admission_exam.university_faculty.display_name,
        'student_name': ' '.join([student.family_name, student.given_name]),
    }
    return render(request, 'admission_exam_db/student_admission_exam_form.html', context)

@login_required
@user_passes_test(is_editor)
def delete_student_admission_exam(request, student_id, student_admission_exam_id):
    student = get_object_or_404(Student, student_id=student_id)
    admission_exam = get_object_or_404(StudentAdmissionExam, id=student_admission_exam_id, student=student)

    # 削除処理
    admission_exam.delete(user=request.user)
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

@login_required
def user(request):
    context = {
        'nbar': 'user',
    }
    return render(request, 'admission_exam_db/user.html', context)
