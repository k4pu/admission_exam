from django.test import TestCase
from .models import Student, UniversityFaculty, StudentAdmissionExam

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

def create_student_admission_exam(
        student,
        university_faculty,
        year_to_take="2025",
        preference="A1",
        result="AE",
        info=""
    ):
        return StudentAdmissionExam.objects.create(
            student=student,
            university_faculty=university_faculty,
            year_to_take=year_to_take,
            preference=preference,
            result=result,
            info=info
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

class StudentAdmissionExamModelTest(TestCase):
    def setUp(self):
        self.student = create_student()
        self.university_faculty = create_university_faculty()

    def test_student_admission_exam_str(self):
        """__str__メソッドの表示のテスト"""
        self.student_admission_exam = create_student_admission_exam(student=self.student, university_faculty=self.university_faculty)
        self.assertEqual(str(self.student_admission_exam), " ".join([self.student.family_name, self.student.given_name]) + ": " + self.university_faculty.display_name)
        
    def test_from_result_to_result_status_P(self):
        """resultからresult_statusが正しくPに設定されるかのテスト"""
        choices = StudentAdmissionExam.PASSED_CHOICES

        result_flag = True
        for choice in choices:
            self.student_admission_exam = create_student_admission_exam(
                    student=self.student,
                    university_faculty=self.university_faculty,
                    result=choice[0]
                )
            if self.student_admission_exam.result_status != "P":
                result_flag = False
        self.assertIs(result_flag, True)

    def test_from_result_to_result_status_R(self):
        """resultからresult_statusが正しくRに設定されるかのテスト"""
        choices = StudentAdmissionExam.REJECTED_CHOICES

        result_flag = True
        for choice in choices:
            self.student_admission_exam = create_student_admission_exam(
                    student=self.student,
                    university_faculty=self.university_faculty,
                    result=choice[0]
                )
            if self.student_admission_exam.result_status != "R":
                result_flag = False
        self.assertIs(result_flag, True)

    def test_from_result_to_result_status_Y(self):
        """resultからresult_statusが正しくYに設定されるかのテスト"""
        choices = StudentAdmissionExam.YET_CHOICES

        result_flag = True
        for choice in choices:
            self.student_admission_exam = create_student_admission_exam(
                    student=self.student,
                    university_faculty=self.university_faculty,
                    result=choice[0]
                )
            if self.student_admission_exam.result_status != "Y":
                result_flag = False
        self.assertIs(result_flag, True)
