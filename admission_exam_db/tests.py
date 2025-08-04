from django.test import TestCase
from .models import Student, UniversityFaculty

def create_student(
        student_id="1234567",
        homeroom_class="1",
        attendance_number="10",
        family_name="田中",
        given_name="太郎",
        family_name_kana="たなか",
        given_name_kana="たろう",
        graduation_year="2025"
    ):
        return Student.objects.create(
            student_id=student_id,
            homeroom_class=homeroom_class,
            attendance_number=attendance_number,
            family_name=family_name,
            given_name=given_name,
            family_name_kana=family_name_kana,
            given_name_kana=given_name_kana,
            graduation_year=graduation_year
        )

def create_university_faculty(
        university_faculty_code="12345",
        university_name="テスト",
        faculty_name="理",
        department_name="数学",
        display_name="テスト_理_数学",
        faculty_system_midstream_name="理",
        faculty_system_field_code="4101",
        faculty_system_field_name="数学・数理情報"
    ):
        return UniversityFaculty.objects.create(
            university_faculty_code=university_faculty_code,
            university_name=university_name,
            faculty_name=faculty_name,
            department_name=department_name,
            display_name=display_name,
            faculty_system_midstream_name=faculty_system_midstream_name,
            faculty_system_field_code=faculty_system_field_code,
            faculty_system_field_name=faculty_system_field_name
        )


class StudentModelTest(TestCase):
    def setUp(self):
        self.student = create_student()
    def test_student_str(self):
        """__str__メソッドの表示のテスト"""
        self.assertEqual(str(self.student), self.student.family_name + " " + self.student.given_name)

class UniversityFacultyModelTest(TestCase):
    def setUp(self):
        self.university_faculty = create_university_faculty()
    def test_university_faculty_str(self):
        """__str__メソッドの表示のテスト"""
        self.assertEqual(str(self.university_faculty), self.university_faculty.display_name)
