from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    family_name = models.CharField(max_length=20)
    given_name = models.CharField(max_length=20)
