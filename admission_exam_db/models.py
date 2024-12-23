from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    family_name = models.CharField(max_length=20)
    given_name = models.CharField(max_length=20)

    def __str__(self):
        return " ".join([self.family_name, self.given_name])

class UniversityFuculty(models.Model):
    university_code = models.CharField(max_length=5, primary_key=True)# 記入用大学コード(５桁)
    university_name = models.CharField(max_length=10)  # 大学短縮名
    faculty_name = models.CharField(max_length=10) # 学部短縮名
    department_name = models.CharField(max_length=20) # 学科短縮名
    display_name = models.CharField(max_length=40) # 秀英用表示名
    faculty_system_midstream_name = models.CharField(max_length=15) # 学部系統(中系統)名称
    faculty_system_field_code = models.CharField(max_length=4) # 学部系統(分野)コード
    faculty_system_field_name = models.CharField(max_length=10) # 学部系統(分野)名称

    def __str__(self):
        return self.department_name
