from django.contrib import admin
from admission_exam_db.models import Student, UniversityFaculty, UniversityFacultyYearlyCode, StudentAdmissionExam

# ここに記入したモデルはadmin pageに表示されるようになる
admin.site.register(Student)
admin.site.register(UniversityFaculty)
admin.site.register(UniversityFacultyYearlyCode)
admin.site.register(StudentAdmissionExam)
