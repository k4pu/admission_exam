from django.db import models
from django.core import validators
import logging
import datetime

logger = logging.getLogger('django')


class Student(models.Model):
    student_id = models.CharField(max_length=7, primary_key=True)
    homeroom_class = models.CharField(max_length=1)
    attendance_number = models.CharField(max_length=2)
    family_name = models.CharField(max_length=30)
    given_name = models.CharField(max_length=30)
    family_name_kana = models.CharField(max_length=30)
    given_name_kana = models.CharField(max_length=30)
    graduation_year = models.CharField(max_length=4)

    def __str__(self):
        return " ".join([self.family_name, self.given_name])

class UniversityFaculty(models.Model):
    university_faculty_code = models.CharField(max_length=5, primary_key=True)# 記入用大学コード(５桁)
    university_name = models.CharField(max_length=20)  # 大学短縮名
    faculty_name = models.CharField(max_length=20) # 学部短縮名
    department_name = models.CharField(max_length=20) # 学科短縮名
    display_name = models.CharField(max_length=50) # 秀英用表示名
    faculty_system_midstream_name = models.CharField(max_length=20) # 学部系統(中系統)名称
    faculty_system_field_code = models.CharField(max_length=4) # 学部系統(分野)コード
    faculty_system_field_name = models.CharField(max_length=20) # 学部系統(分野)名称

    def __str__(self):
        return self.display_name

class StudentAdmissionExam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    university_faculty = models.ForeignKey(UniversityFaculty, on_delete=models.CASCADE)
    year_to_take = models.CharField(max_length=4)
    PREFERENCE_CHOICES = [
        ('A1','受かったら必ず入学する第1志望'),
        ('A2','受かったら必ず入学する第2志望'),
        ('A3','受かったら必ず入学する第3志望'),
        ('A4','受かったら必ず入学する第4志望'),
        ('A5','受かったら必ず入学する第5志望'),
        ('A6','受かったら必ず入学する第6志望'),
        ('A7','受かったら必ず入学する第7志望'),
        ('A8','受かったら必ず入学する第8志望'),
        ('A9','受かったら必ず入学する第9志望'),
        ('A10','受かったら必ず入学する第10志望'),
        ('B','状況によって入学を検討する'),
        ('C','受かっても入学しない'),
    ]
    RESULT_CHOICES = [
        ('AE','合格（入学）'),
        ('FASN','前期合格で後期受験せず'),
        ('AN','合格（入学せず）'),
        ('ASE','合格（特待、入学）'),
        ('ASN','合格（特待、入学せず）'),
        ('OP','他志望で合格'),
        ('AAE','追加合格（不合格から合格）して入学'),
        ('AAN','追加合格（不合格から合格）して入学せず'),
        ('SAE','補欠合格（補欠から合格）して入学'),
        ('SAN','補欠合格（補欠から合格）して入学せず'),
        ('S','補欠'),
        ('R','不合格'),
        ('1A2N','1次合格2次受験せず'),
        ('1A2R','1次合格2次不合格'),
        ('1R','1次不合格'),
        ('CN','共通テスト後出願せず'),
        ('N','受験せず（受験番号あり）'),
        ('NA','出願せず（受験番号なし）'),
        ('REAN','推薦、総合型で合格したので受験せず'),
    ]
    preference = models.CharField( # 志望
        max_length=3,
        choices=PREFERENCE_CHOICES,
        null=False,
        blank=False
    )
    result = models.CharField(
        max_length=4,
        choices=RESULT_CHOICES,
        null=True,
        blank=True
    )
    info = models.CharField( #備考
        max_length=200,
        null=True,
        blank=True
    )

    def __str__(self):
        return " ".join([self.student.family_name, self.student.given_name]) + ": " + self.university_faculty.display_name

    def save(self, user=None, *args, **kwargs):
        is_new = self.pk is None  # 既存のデータであればpkが存在

        super().save(*args, **kwargs)

        if is_new:
            logger.info(f"Created New Object: {self}, New Object ID Assigned: {self.pk}, Created By User ID: {user.id if user else 'Anonymous'}")
        else:
            logger.info(f"Updated Object: {self}, Object ID: {self.pk}, Updated By User ID: {user.id if user else 'Anonymous'}")
    def delete(self, user=None, *args, **kwargs):
        object_id = self.pk
        super().delete(*args, **kwargs)

        # ログに記録
        logger.info(f"Deleted Object: {self.__class__.__name__}, Object ID: {object_id}, Deleted By User ID: {user.id if user else 'Anonymous'}")

