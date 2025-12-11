from django import forms
from .models import UniversityFaculty, UniversityFacultyYearlyCode, StudentAdmissionExam
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
        fields = ['year_to_take', 'preference', 'result', 'info']# yearly_university_facultyを採用してからここにuniversity_facultyを入れてしまうと不都合があることがわかった
        labels = {
            'year_to_take': '入試年度',
            'preference': '志望',
            'result': '結果',
            'info': '備考',
        }
        widgets = {
            'year_to_take': forms.NumberInput(attrs={
                'id': 'year-to-take',
                'name': 'year_to_take',
                'class': 'Form-Item-Choice',
            }),
            'preference': forms.Select(attrs={
                'class': 'Form-Item-Choice',
            }),
            'result': forms.Select(attrs={
                'class': 'Form-Item-Choice',
            }),
            'info': forms.Textarea(attrs={
                'class': 'Form-Item-Textarea',
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
        instance = super().save(commit=False)# 一旦親クラスのsaveメソッドでStudentAdmissionExamインスタンスを作成する. この時点でデータベースに反映はされない
        year_to_take = self.cleaned_data.get('year_to_take')
        if self.student:
            instance.student = self.student # Noneの場合もあるが、そうでなければinstanceにstudentを代入する
        university_faculty_code = self.data.get('university_faculty_code')# ブラウザのinputの情報を取得
        if university_faculty_code:
            yearly_university_faculty = UniversityFacultyYearlyCode.objects.get(
                year=year_to_take,
                university_faculty_code=university_faculty_code
            )
            instance.university_faculty = yearly_university_faculty.university_faculty

        if commit:
            instance.save(user=user)# save()はdefaultでcommit=Trueなのでここでデータベースに保存される
        return instance# 親クラスもinstanceを返すし, この方が良さそうではあるが使い道はまだわからない -> views.py のcreate_student_admission_examのform = StudentAdmissionExamForm()で受け取るのか
