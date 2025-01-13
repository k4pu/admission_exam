from django.urls import path, include

from . import views

app_name = "admission_exam_db"
urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("student/", views.student, name="student"),
    path("student/<int:student_id>", views.student_detail, name="student_detail"),
    path("upload_university_faculty", views.upload_university_faculty, name="upload_university_faculty"),
    path("upload_student", views.upload_student, name="upload_student"),
    path("student/<int:student_id>/create_student_admission_exam", views.create_student_admission_exam, name="create_student_admission_exam"),
    path("api/university_faculty", views.university_faculty_autocomplete, name="university_faculty_autocomplete"),
]
