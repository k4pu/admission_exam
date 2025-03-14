from django.urls import path, include

from . import views

app_name = "admission_exam_db"
urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("user/", views.user, name="user"),
    path("student/", views.student, name="student"),
    path("student/<int:student_id>", views.student_detail, name="student_detail"),
    path("upload_university_faculty", views.upload_university_faculty, name="upload_university_faculty"),
    path("download_template_csv/<str:file_kind>", views.download_template_csv, name="download_template_csv"),
    path("download_data", views.download_data, name="download_data"),
    path("download_data/csv/<str:file_kind>", views.download_data_csv, name="download_data_csv"),
    path("upload_student", views.upload_student, name="upload_student"),
    path("upload_student_admission_exam", views.upload_student_admission_exam, name="upload_student_admission_exam"),
    path("upload_user", views.upload_user, name="upload_user"),
    path("upload_success", views.upload_success, name="upload_success"),
    path("student/<int:student_id>/create_student_admission_exam", views.create_student_admission_exam, name="create_student_admission_exam"),
    path("student/<int:student_id>/<int:student_admission_exam_id>", views.edit_student_admission_exam, name="edit_student_admission_exam"),
    path("student/<int:student_id>/<int:student_admission_exam_id>/delete", views.delete_student_admission_exam, name="delete_student_admission_exam"),
    path("admission_exam/", views.admission_exam, name="admission_exam"),
    path("passed_exam_count/", views.passed_exam_count, name="passed_exam_count"),
    path("api/university_faculty", views.university_faculty_autocomplete, name="university_faculty_autocomplete"),
]
