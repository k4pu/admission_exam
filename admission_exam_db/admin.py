from django.contrib import admin
from admission_exam_db.models import Student, UniversityFaculty, StudentAdmissionExam

admin.site.register(Student)
admin.site.register(UniversityFaculty)
admin.site.register(StudentAdmissionExam)
