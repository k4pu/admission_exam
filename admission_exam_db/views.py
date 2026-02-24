from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.db.models import IntegerField
from django.db.models.functions import Cast
from .forms import UniversityFacultyCSVUploadForm, StudentCSVUploadForm, UserCSVUploadForm, StudentAdmissionExamForm, StudentAdmissionExamCSVUploadForm

from .models import Student, UniversityFaculty, UniversityFacultyYearlyCode, StudentAdmissionExam
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.db.models import Q, F, Count, Min

import csv
import io
import logging
import datetime

logger = logging.getLogger('django')


def is_admin(user): # userがadmin userかどうかを返す
    return user.is_superuser

def is_editor(user): # userがeditor userかどうかを返す
    if user.groups.filter(name="editor").exists() or user.is_superuser: # userがeditor groupに所属しているかsuper_userであればTrue
        return True
    else: # それ以外がFalse
        return False

@login_required # ログイン後でないとアクセスできない
def index(request): # index pageのview ホームのpage
    context = { # templateの中で使いたい情報
        'nbar': 'home',
    }
    return render(request, "admission_exam_db/index.html", context)

@login_required # ログイン後でないとアクセスできない
def student(request): # student pageのview 生徒一覧page
    student_list = Student.objects.annotate( # 生徒リストを卒業年, クラス, 出席番号順に取得
            order_attendance_number=Cast( # attendance_number自体は文字列扱いなので辞書式でなく数値として正しい順に表示するためにcastする
                "attendance_number",
                IntegerField()
            )
        ).order_by("-graduation_year", "homeroom_class", "order_attendance_number")
    context ={ # templateの中で使いたい情報
        'nbar': 'student',
        'student_list': student_list,
    }
    return render(request, "admission_exam_db/student.html", context)

@login_required # ログイン後でないとアクセスできない
def admission_exam(request): # admission_exam pageのview 受験リストのpage
    admission_exam_list = StudentAdmissionExam.objects.order_by("-year_to_take", "university_faculty_id") # 受験リストを年度の降順, 大学学部id順に取得
    passed_choices = [ {"key":key, "value":value} for key, value in StudentAdmissionExam.PASSED_CHOICES ]
    rejected_choices = [ {"key":key, "value":value} for key, value in StudentAdmissionExam.REJECTED_CHOICES ]
    yet_choices = [ {"key":key, "value":value} for key, value in StudentAdmissionExam.YET_CHOICES ]
    context ={ # templateの中で使いたい情報
        'nbar': 'admission_exam',
        'admission_exam_list': admission_exam_list,
        'passed_choices': passed_choices,
        'rejected_choices': rejected_choices,
        'yet_choices': yet_choices,
    }
    return render(request, "admission_exam_db/admission_exam.html", context)

@login_required # ログイン後でないとアクセスできない
def passed_exam_count(request): # passed_exam_count の view 大学合格者数のpage
    student_admission_exam = StudentAdmissionExam.objects.filter(result_status="P").all()
    years = sorted(list({ dic["year_to_take"] for dic in student_admission_exam.values("year_to_take") }), reverse=True)
    passed_exam_count_table = {
        year: {}
        for year in years
    }

    for year in years:
        university_faculty_list = UniversityFaculty.objects.filter(
            studentadmissionexam__year_to_take=year,
            studentadmissionexam__result_status="P"
        ).values(
            "studentadmissionexam__year_to_take",
            "university_name",
            "faculty_name"
        ).annotate(
            passed_exam_count=Count("studentadmissionexam", distinct=True),
            passed_exam_count_by_graduates=Count(
                "studentadmissionexam",
                filter=Q(studentadmissionexam__student__graduation_year__lt=F("studentadmissionexam__year_to_take")),
                distinct=True
            ),
            order_code=Min("university_faculty_yearly_codes__university_faculty_code"),
        ).filter(passed_exam_count__gt=0).order_by("order_code")

        university_name_list = university_faculty_list.values("university_name").order_by("university_faculty_yearly_codes__university_faculty_code")

        passed_exam_count_table[year] = {
            university_name['university_name']: {}
            for university_name in university_name_list
        }
        for faculty in university_faculty_list:
            passed_exam_count_table[year][faculty["university_name"]][faculty["faculty_name"]] = {'total':faculty["passed_exam_count"], 'graduates':faculty["passed_exam_count_by_graduates"]}

    context ={ # templateの中で使いたい情報
        'passed_exam_count_table': passed_exam_count_table,
        'nbar': 'passed_exam_count',
    }
    return render(request, "admission_exam_db/passed_exam_count.html", context)

@login_required # ログイン後でないとアクセスできない
def passed_exam_by_university(request, exam_year, university): # 大学別合格一覧ページ 大学合格者数ページから飛んでこれるページ
    admission_exam_list = StudentAdmissionExam.objects.filter(university_faculty__university_name=university, year_to_take=exam_year, result_status="P", university_faculty__university_faculty_yearly_codes__year=exam_year).order_by("university_faculty__university_faculty_yearly_codes__university_faculty_code", "-student__graduation_year")
    context ={ # templateの中で使いたい情報
        'nbar': 'passed_exam_count',
        'exam_year': exam_year,
        'university': university,
        'admission_exam_list': admission_exam_list,
    }
    return render(request, "admission_exam_db/passed_exam_by_university.html", context)

@login_required # ログイン後でないとアクセスできない
def student_detail(request, student_id): # 生徒別受験詳細ページ
    student = get_object_or_404(Student, student_id=student_id)

    current_num = int(student.attendance_number) # 現在の生徒の出席番号を一時的に数値化

    base = Student.objects.annotate(
        order_attendance_number=Cast("attendance_number", IntegerField()) # 文字列だが一時的に数値として扱う仮想カラムを追加
    ).filter(
        graduation_year=student.graduation_year
    )

    prev_student = base.filter(
        Q(homeroom_class__lt=student.homeroom_class) |
        Q(homeroom_class=student.homeroom_class, order_attendance_number__lt=current_num)
    ).order_by('-homeroom_class', '-order_attendance_number').first()

    next_student = base.filter(
        Q(homeroom_class__gt=student.homeroom_class) |
        Q(homeroom_class=student.homeroom_class, order_attendance_number__gt=current_num)
    ).order_by('homeroom_class', 'order_attendance_number').first()

    student_admission_exam_list = StudentAdmissionExam.objects.filter(
        student=student,
    ).annotate(
        order_code=Min("university_faculty__university_faculty_yearly_codes__university_faculty_code"),
    ).order_by("-year_to_take", "order_code")

    context ={ # templateの中で使いたい情報
        'nbar': 'student_detail',
        'student_id': student_id,
        'homeroom_class': student.homeroom_class,
        'attendance_number': student.attendance_number,
        'student_name': ' '.join([student.family_name, student.given_name]),
        'prev_student': prev_student,
        'next_student': next_student,
        'student_admission_exam_list': student_admission_exam_list,
    }
    return render(request, "admission_exam_db/student_detail.html", context)

@login_required # ログイン後でないとアクセスできない
@user_passes_test(is_admin) # admin user でないとアクセスできない
def upload_university_faculty(request): # 大学・学部データアップロードページ
    if request.method == "POST":
        form = UniversityFacultyCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                year = row['year']
                university_faculty_code = row['university_faculty_code']
                university_name = row['university_name']
                faculty_name = row['faculty_name']
                department_name = row['department_name']
                faculty_system_midstream_code = row['faculty_system_midstream_code']
                faculty_system_midstream_name = row['faculty_system_midstream_name']
                faculty_system_field_code = row['faculty_system_field_code']
                faculty_system_field_name = row['faculty_system_field_name']

                # university_name, faculty_name, department_nameがすでに登録済ならそのfacultyを取得
                # そうでなければ作成して取得
                # そのfaculty, year, university_faculty_codeをもつデータを作成
                faculty, _ = UniversityFaculty.objects.get_or_create(
                    university_name=university_name,
                    faculty_name=faculty_name,
                    department_name=department_name,
                    defaults = {
                        'faculty_system_midstream_code': faculty_system_midstream_code,
                        'faculty_system_midstream_name': faculty_system_midstream_name,
                        'faculty_system_field_code': faculty_system_field_code,
                        'faculty_system_field_name': faculty_system_field_name,
                    }
               )

                # データモデルに保存
                UniversityFacultyYearlyCode.objects.update_or_create(
                    year=year,
                    university_faculty=faculty,
                    defaults={
                        'university_faculty_code': university_faculty_code,
                    }
                )
            return redirect('admission_exam_db:upload_success') # アップロード成功画面にリダイレクト
    else:
        form = UniversityFacultyCSVUploadForm()
    context = { # templateの中で使いたい情報
        'nbar': 'upload_university_faculty',
        'form': form,
    }
    return render(request, 'admission_exam_db/upload_university_faculty.html', context)

@login_required # ログイン後でないとアクセスできない
def download_template_csv(request, file_kind): # アップロード用のテンプレートcsvのダウンロードページ
    filename = f"{file_kind}_template.csv"

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    if file_kind == "university_faculty":
        writer.writerow(["year", "university_faculty_code", "university_name", "faculty_name", "department_name", "faculty_system_midstream_code", "faculty_system_midstream_name", "faculty_system_field_code", "faculty_system_field_name"])
        writer.writerow(["2025", "10001", "旭川医科" ,"医" ,"医－前", "51", "医・歯・薬・保健" ,"5101" ,"医"])
    elif file_kind == "student":
        writer.writerow(["student_id", "homeroom_class", "attendance_number", "gender", "family_name", "given_name", "family_name_kana", "given_name_kana", "graduation_year"])
        writer.writerow(["1900123", "A", "01", "M", "佐藤", "花子", "さとう", "はなこ", "2025"])
    elif file_kind == "user":
        writer.writerow(["username", "password", "email", "is_editor"])
        writer.writerow(["test", "testpass", "test@example.ed.jp", "True"])
    elif file_kind == "student_admission_exam":
        writer.writerow(["student_admission_exam_id", "student_id", "university_faculty_code", "year_to_take", "preference", "result", "info"])
        writer.writerow(["30", "1990123", "10001", "2025", "A1", "AE", "備考など"])

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

@login_required # ログイン後でないとアクセスできない
@user_passes_test(is_editor) # editor userでないとアクセスできない
def download_data_csv(request, file_kind): # データのダウンロード用view
    filename = f"{file_kind}_data.csv"

    if file_kind == "student":
        student_list = Student.objects.order_by("homeroom_class", "attendance_number")

        header_row = [["student_id", "homeroom_class", "attendance_number", "gender", "family_name", "given_name", "family_name_kana", "given_name_kana", "graduation_year"]]
        data_rows = [[student.student_id, student.homeroom_class, student.attendance_number, student.gender, student.family_name, student.given_name, student.family_name_kana, student.given_name_kana, student.graduation_year] for student in student_list]

    elif file_kind == "university_faculty":
        faculty_list = UniversityFaculty.objects.order_by("id")

        header_row = [["id", "university_name", "faculty_name", "department_name", "faculty_system_midstream_code", "faculty_system_midstream_name", "faculty_system_field_code", "faculty_system_field_name"]]
        data_rows = [[faculty.id, faculty.university_name, faculty.faculty_name, faculty.department_name, faculty.faculty_system_midstream_code, faculty.faculty_system_midstream_name, faculty.faculty_system_field_code, faculty.faculty_system_field_name] for faculty in faculty_list]

    elif file_kind == "university_faculty_yearly_code":
        faculty_list = UniversityFacultyYearlyCode.objects.order_by("university_faculty_code")

        header_row = [["yearly_code_id", "university_faculty_id", "year", "university_faculty_code"]]
        data_rows = [[faculty.id, faculty.university_faculty.id, faculty.year, faculty.university_faculty_code] for faculty in faculty_list]

    elif file_kind == "joined_university_faculty":
        faculty_list = UniversityFacultyYearlyCode.objects.order_by("university_faculty_code")

        header_row = [["year", "university_faculty_code", "university_name", "faculty_name", "department_name", "faculty_system_midstream_name", "faculty_system_field_code", "faculty_system_field_name"]]
        data_rows = [[faculty.year, faculty.university_faculty_code, faculty.university_faculty.university_name, faculty.university_faculty.faculty_name, faculty.university_faculty.department_name, faculty.university_faculty.faculty_system_midstream_name, faculty.university_faculty.faculty_system_field_code, faculty.university_faculty.faculty_system_field_name] for faculty in faculty_list]

    elif file_kind == "student_admission_exam":
        admission_exam_list = StudentAdmissionExam.objects.order_by("id")# TODO これはより良いorderがありそうなので考える
        header_row = [["student_admission_exam_id", "student_id", "university_faculty_code", "year_to_take", "preference", "result", "result_status", "info"]]
        data_rows = [[exam.id, exam.student.student_id, exam.university_faculty.university_faculty_yearly_codes.get(year=exam.year_to_take).university_faculty_code, exam.year_to_take, exam.preference, exam.result, exam.result_status, exam.info] for exam in admission_exam_list]

    elif file_kind == "student_admission_exam_display":
        admission_exam_list = StudentAdmissionExam.objects.order_by(
            "year_to_take",
            "student__homeroom_class",
            "student__attendance_number",
            "university_faculty__pk"
        )# TODO これはより良いorderがありそうなので考える
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

@login_required # ログイン後でないとアクセスできない
def download_data(request): # データのダウンロード選択page
    context = { # templateの中で使いたい情報
        'nbar': 'download_data',
    }
    return render(request, "admission_exam_db/download_data.html", context)

@login_required # ログイン後でないとアクセスできない
@user_passes_test(is_admin) # admin user でないとアクセスできない
def upload_student(request): # 生徒のデータアップロードページ
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
                gender = row['gender']
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
                        'gender': gender,
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
    context = { # templateの中で使いたい情報
        'nbar': 'upload_student',
        'form': form,
    }
    return render(request, 'admission_exam_db/upload_student.html', context)

@login_required # ログイン後でないとアクセスできない
@user_passes_test(is_admin) # admin user でないとアクセスできない
def upload_user(request): # ユーザのデータアップロードページ
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
                        email = row['email']# TODO 不要か?
                        is_editor = True if row['is_editor'].lower() == "true" else False

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

                        if is_editor:
                            group = Group.objects.get(name='editor')
                            user.groups.add(group)

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
    context = { # templateの中で使いたい情報
        'nbar': 'upload_user',
        'form': form,
    }
    return render(request, 'admission_exam_db/upload_user.html', context)

def upload_success(request): # アップロード成功page
    context = {} # templateの中で使いたい情報
    return render(request, 'admission_exam_db/upload_success.html', context)

@login_required # ログイン後でないとアクセスできない
@user_passes_test(is_admin) # admin user でないとアクセスできない
def upload_student_admission_exam(request): # 受験データアップロードpage
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
                info = row['info']

                student = get_object_or_404(Student, student_id=student_id)
                university_faculty_yearly_code = get_object_or_404(UniversityFacultyYearlyCode, year=year_to_take, university_faculty_code=university_faculty_code)
                university_faculty = university_faculty_yearly_code.university_faculty
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
                        'info': info,
                        }
                    )
                else:
                    StudentAdmissionExam.objects.create(
                        student=student,
                        university_faculty=university_faculty,
                        year_to_take=year_to_take,
                        preference=preference,
                        result=result,
                        info=info,
                    )

            return redirect('admission_exam_db:upload_success') # アップロード成功画面にリダイレクト
    else:
        form = StudentAdmissionExamCSVUploadForm()
    context = { # templateの中で使いたい情報
        'nbar': 'upload_student_admission_exam',
        'form': form,
    }
    return render(request, 'admission_exam_db/upload_student_admission_exam.html', context)

@login_required # ログイン後でないとアクセスできない
@user_passes_test(is_editor) # editor userでないとアクセスできない
def create_student_admission_exam(request, student_id): # 生徒受験データ作成page
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        form = StudentAdmissionExamForm(request.POST, student=student)# 生徒はすでに指定しているので、formで新たに入力する手間を省くためにstudentオブジェクトを渡す
        if form.is_valid():

            form.save(user=request.user)
            return redirect('admission_exam_db:student_detail', student_id=student_id)
    else:
        form = StudentAdmissionExamForm(student=student)# studentオブジェクトを渡す

    context ={ # templateの中で使いたい情報
        'nbar': 'student',
        'form': form,
        'student_id': student_id,
        'student_name': ' '.join([student.family_name, student.given_name]),
    }
    return render(request, 'admission_exam_db/student_admission_exam_form.html', context)

@login_required # ログイン後でないとアクセスできない
@user_passes_test(is_editor) # editor userでないとアクセスできない
def edit_student_admission_exam(request, student_id, student_admission_exam_id): # 生徒受験データ編集page
    student = get_object_or_404(Student, student_id=student_id)
    admission_exam = get_object_or_404(StudentAdmissionExam, id=student_admission_exam_id, student=student)

    if request.method == 'POST':
        form = StudentAdmissionExamForm(request.POST, instance=admission_exam)
        if form.is_valid():

            form.save(commit=True, user=request.user)
            return redirect('admission_exam_db:student_detail', student_id=student_id)

    else:
        form = StudentAdmissionExamForm(instance=admission_exam)

    context = { # templateの中で使いたい情報
        'nbar': 'student',
        'form': form,
        'student_id': student_id,
        'student_admission_exam_id': student_admission_exam_id,
        'university_faculty_display_name': admission_exam.university_faculty.display_name,
        'student_name': ' '.join([student.family_name, student.given_name]),
    }
    return render(request, 'admission_exam_db/student_admission_exam_form.html', context)

@login_required # ログイン後でないとアクセスできない
@user_passes_test(is_editor) # editor userでないとアクセスできない
def delete_student_admission_exam(request, student_id, student_admission_exam_id): # 生徒受験データ削除画面
    student = get_object_or_404(Student, student_id=student_id)
    admission_exam = get_object_or_404(StudentAdmissionExam, id=student_admission_exam_id, student=student)

    # 削除処理
    admission_exam.delete(user=request.user)
    messages.success(request, "受験データ削除に成功しました")

    return redirect('admission_exam_db:student_detail', student_id=student_id)


@login_required # ログイン後でないとアクセスできない
def university_faculty_autocomplete(request): # 大学学部オートコンプリートpage
    query = request.GET.get('q', '') # クエリパラメータ 'q' を取得
    year = request.GET.get('y', '') # クエリパラメータ 'year' を取得
    if query:
        yearlyfaculties = UniversityFacultyYearlyCode.objects.filter(year__exact=year).filter(
                Q(university_faculty__display_name__startswith=query) | Q(university_faculty_code__startswith=query)
            )[:100]
    else:
        yearlyfaculties = UniversityFacultyYearlyCode.objects.none()
    results = [{"code": faculty.university_faculty_code, "name": faculty.university_faculty.display_name} for faculty in yearlyfaculties]
    return JsonResponse(results, safe=False)

@login_required # ログイン後でないとアクセスできない
def user(request): # ユーザーpage
    context = { # templateの中で使いたい情報
        'nbar': 'user',
    }
    return render(request, 'admission_exam_db/user.html', context)
