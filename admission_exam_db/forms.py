from django import forms
from .models import UniversityFaculty, StudentAdmissionExam

class UniversityFacultyCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class StudentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class StudentAdmissionExamForm(forms.ModelForm):
    class Meta:
        model = StudentAdmissionExam
        fields = ['university_faculty', 'preference', 'result']
        labels = {
            'university_faculty': '大学・学部コード',
            'preference': '志望',
            'result': '結果',
        }
        widgets = {
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

    def save(self, commit=True):
        instance = super().save(commit=False)# 一旦親クラスのsaveメソッドでStudentAdmissionModelインスタンスを作成する. この時点でデータベースに反映はされない
        if self.student:
            instance.student = self.student # Noneの場合もあるが、そうでなければinstanceにstudentを代入する
        if commit:
            instance.save()# save()はdefaultでcommit=Trueなのでここでデータベースに保存される
        return instance# 親クラスもinstanceを返すし, この方が良さそうではあるが使い道はまだわからない
