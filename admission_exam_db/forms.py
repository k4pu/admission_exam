from django import forms
from .models import UniversityFaculty

class UniversityFacultyCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')
