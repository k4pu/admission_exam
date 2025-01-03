from django import forms
from .models import UniversityFaculty, StudentAdmissionExam

class UniversityFacultyCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class StudentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class StudentAdmissionExamForm(forms.ModelForm):
    class Meta:
        model = StudentAdmissionExam
        fields = ['student', 'university_faculty', 'preference', 'result']
        labels = {
            'student': '生徒',
            'university_faculty': '大学・学部',
            'preference': '志望',
            'result': '結果',
        }
