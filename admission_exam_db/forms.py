from django import forms
from .models import UniversityFaculty, StudentAdmissionExam
import datetime


class StudentAdmissionExamCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class UniversityFacultyCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class StudentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class UserCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class StudentAdmissionExamForm(forms.ModelForm):
    class Meta:
        model = StudentAdmissionExam
        fields = ['year_to_take', 'university_faculty', 'preference', 'result']
        labels = {
            'year_to_take': '入試年度',
            'university_faculty': '大学・学部コード',
            'preference': '志望',
            'result': '結果',
        }
        widgets = {
            'year_to_take': forms.NumberInput(attrs={
                'class': 'Form-Item-Choice',
            }),
            'university_faculty': forms.TextInput(attrs={
                'id': 'university-faculty-autocomplete',
                'class': 'Form-Item-Input',
                'autocomplete': 'off',
                'placeholder': '大学・学部名またはコードを入力',
            }),
            'preference': forms.Select(attrs={
                'class': 'Form-Item-Choice',
            }),
            'result': forms.Select(attrs={
                'class': 'Form-Item-Choice',
            }),
        }

    def __init__(self, *args, **kwargs):# インスタンス作成時の引数はここで受け取れば良いのか
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        dt = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        ) + datetime.timedelta(days=180)# 半年ぐらい足しとけばちょうどいい？
        default_exam_year = dt.year
        self.fields['year_to_take'].initial = default_exam_year

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)# 一旦親クラスのsaveメソッドでStudentAdmissionModelインスタンスを作成する. この時点でデータベースに反映はされない
        if self.student:
            instance.student = self.student # Noneの場合もあるが、そうでなければinstanceにstudentを代入する
        university_faculty_id = self.data.get('university_faculty_id')
        if university_faculty_id:
            instance.university_faculty_id = university_faculty_id

        if commit:
            instance.save(user=user)# save()はdefaultでcommit=Trueなのでここでデータベースに保存される
        return instance# 親クラスもinstanceを返すし, この方が良さそうではあるが使い道はまだわからない
