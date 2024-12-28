from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("students/", views.students, name="students"),
    path("students/<int:student_id>", views.student_detail, name="student_detail"),
    path("upload_university_faculty", views.upload_university_faculty, name="upload_university_faculty"),
    path("upload_student", views.upload_student, name="upload_student"),
]
