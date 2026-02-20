from django.db import models
from django.core import validators
import logging
import datetime

logger = logging.getLogger('django')


class Student(models.Model): # 生徒モデル
    student_id = models.CharField(max_length=7, primary_key=True) # 生徒の学籍番号7桁 # TODO student_idよりidのほうが良かったなあ
    homeroom_class = models.CharField(max_length=1) # ホームルームクラス'A, B, .. など'
    attendance_number = models.CharField(max_length=2) # 生徒の出席番号 # ここを数値（PositiveSmallIntegerなど）扱いにしたいが、運用が始まったのでおいておく
    family_name = models.CharField(max_length=30) # 姓
    given_name = models.CharField(max_length=30) # 名
    family_name_kana = models.CharField(max_length=30) # 姓 ふりがな
    given_name_kana = models.CharField(max_length=30) # 名 ふりがな
    graduation_year = models.CharField(max_length=4) # 卒業年 これは受験年と合わせるためにあえて卒業「年度」にしていない 2025年4月に3年生になった生徒のgraduation_yearは2026
    gender = models.CharField( # 性別
        max_length=1,
        choices=[
            ('M', '男性'),
            ('F', '女性')
        ],
        null=True,
        blank=True
    )

    def __str__(self): # このmodelのinstanceをそのまま呼び出したときの表示
        return " ".join([self.family_name, self.given_name]) # "田中 太郎"と表示

class UniversityFaculty(models.Model): # 大学・学部モデル
    id = models.BigAutoField(primary_key=True)
    university_name = models.CharField(max_length=20)  # 大学短縮名
    faculty_name = models.CharField(max_length=20) # 学部短縮名
    department_name = models.CharField(max_length=20) # 学科短縮名
    display_name = models.CharField(max_length=50, null=True, blank=True) # 表示名
    faculty_system_midstream_code = models.CharField(max_length=2) # 学部系統(中系統)コード
    faculty_system_midstream_name = models.CharField(max_length=20) # 学部系統(中系統)名称
    faculty_system_field_code = models.CharField(max_length=4) # 学部系統(分野)コード
    faculty_system_field_name = models.CharField(max_length=20) # 学部系統(分野)名称

    class Meta:
        constraints = [ # 大学名・学部名・学科名全てが同じものは複数存在できない制約
            models.UniqueConstraint(
                fields=['university_name', 'faculty_name', 'department_name'],
                name='uniq_university_faculty_department_name',
            ),
        ]

    def save(self, *args, **kwargs): # display_name というfieldは大学名・学部名・学科名から導かれるもの（旭川医科_医_医など）なので整合性のために直接入力させない
        univ_name = self.university_name
        fac_name = '' if self.faculty_name == '' else '_' + self.faculty_name
        dep_name = '' if self.department_name == '' else '_' + self.department_name
        self.display_name = f"{univ_name}{fac_name}{dep_name}"
        super().save(*args, **kwargs)

    def __str__(self): # このmodelのinstanceをそのまま呼び出したときの表示
        return self.display_name

class UniversityFacultyYearlyCode(models.Model): # 年別の大学・学部コードの一覧
    id = models.BigAutoField(primary_key=True)
    university_faculty = models.ForeignKey(UniversityFaculty, on_delete=models.CASCADE, related_name="university_faculty_yearly_codes") # 大学・学部モデルの参照
    year = models.CharField(max_length=4) # 年（これは受験年）2026年2月に試験を受ける年の学部コードのyearは2026
    university_faculty_code = models.CharField(max_length=5)# 記入用大学コード(５桁)

    class Meta:
        constraints = [
            models.UniqueConstraint( # 同じ年に同じ大学・学部が複数存在できない制約
                fields=['year', 'university_faculty'],
                name='uniq_year_faculty',
            ),
            models.UniqueConstraint( # 同じ年に同じ大学・学部コードが複数存在できない制約
                fields=['year', 'university_faculty_code'],
                name='uniq_year_faculty_code',
            ),
        ]

    def __str__(self): # このmodelのinstanceをそのまま呼び出したときの表示
        return " ".join([self.university_faculty.display_name, self.year])


class StudentAdmissionExam(models.Model): # 生徒の受験モデル '田中太郎が2026年に東京大学理科I類を受験する'など
    student = models.ForeignKey(Student, on_delete=models.CASCADE) # 生徒モデルの参照
    university_faculty = models.ForeignKey( # 大学・学部モデルの参照
        UniversityFaculty,
        on_delete=models.CASCADE,
    )# university_faculty_yearly_codesにつなげるべき？集計時にfilterかけるときに二度手間感
    year_to_take = models.CharField(max_length=4) # 受験年
    PREFERENCE_CHOICES = [ # 志望
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
    PASSED_CHOICES = [ # 受験結果のうち合格ステータスのもの
        ('AE','合格（入学）'),
        ('AN','合格（入学せず）'),
        ('ASE','合格（特待、入学）'),
        ('ASN','合格（特待、入学せず）'),
        ('OP','他志望で合格'),
        ('AAE','追加合格（不合格から合格）して入学'),
        ('AAN','追加合格（不合格から合格）して入学せず'),
        ('SAE','補欠合格（補欠から合格）して入学'),
        ('SAN','補欠合格（補欠から合格）して入学せず'),
    ]
    REJECTED_CHOICES = [ # 受験結果のうち不合格ステータスのもの
        ('R','不合格'),# Rejectedのつもりやったけど, Failedの方が自然やったみたい.更新しよか迷う.
        ('FASN','前期合格で後期受験せず'),
        ('1A2N','1次合格2次受験せず'),
        ('1A2R','1次合格2次不合格'),
        ('1R','1次不合格'),
        ('CN','共通テスト後出願せず'),
        ('N','受験せず（受験番号あり）'),
        ('NA','出願せず（受験番号なし）'),
        ('REAN','推薦、総合型で合格したので受験せず'),
    ]
    YET_CHOICES = [ # 受験結果のうち合否が未定のもの
        ('S','補欠'),
    ] + [('None', 'None')]
    RESULT_CHOICES = PASSED_CHOICES + REJECTED_CHOICES + YET_CHOICES # 受験結果全て

    RESULT_STATUS_CHOICES = [ # 合格ステータス（細かいものではなく合格不合格のみの粗いもの）
        ('P','合格'),
        ('R','不合格'),
        ('Y','未定'),
    ]
    preference = models.CharField( # 志望フィールド
        max_length=3,
        choices=PREFERENCE_CHOICES,
        null=False,
        blank=False
    )
    result = models.CharField( # 受験結果フィールド
        max_length=4,
        choices=RESULT_CHOICES,
        null=True,
        blank=True
    )
    result_status = models.CharField( # 受験結果ステータスフィールド
        max_length=1,
        choices=RESULT_STATUS_CHOICES,
        null=True,
        blank=True
    )
    info = models.CharField( # 備考フィールド
        max_length=200,
        null=True,
        blank=True
    )

    # class Meta:
    #     # ここは運用上外したほうが良い場合がある可能性
    #     constraints = [
    #         models.UniqueConstraint( # 同じ生徒が同じ年に同じ大学・学部を受験しない制約
    #             fields=['student', 'year_to_take', 'university_faculty'],
    #             name='uniq_student_year_exam',
    #         ),
    #     ]

    def __str__(self): # このmodelのinstanceをそのまま呼び出したときの表示
        return " ".join([self.student.family_name, self.student.given_name]) + ": " + self.university_faculty.display_name

    def save(self, user=None, *args, **kwargs):
        is_new = self.pk is None  # 既存のデータであればpkが存在

        # result_categoryの設定
        if self.result in [key for key, _ in self.PASSED_CHOICES]:
            self.result_status = 'P'
        elif self.result in [key for key, _ in self.REJECTED_CHOICES]:
            self.result_status = 'R'
        elif self.result in [key for key, _ in self.YET_CHOICES]:
            self.result_status = 'Y'
        else:
            pass # Exceptionをthrowした方が良さそう

        super().save(*args, **kwargs)

        if is_new: # 受験データが作成された時のログ
            logger.info(f"Created New Object: {self}, New Object ID Assigned: {self.pk}, Created By User ID: {user.id if user else 'Anonymous'}")
        else: # 受験データが更新されたときのログ
            logger.info(f"Updated Object: {self}, Object ID: {self.pk}, Updated By User ID: {user.id if user else 'Anonymous'}")
    def delete(self, user=None, *args, **kwargs):
        object_id = self.pk
        super().delete(*args, **kwargs)

        # 受験データが削除されたときのログ
        logger.info(f"Deleted Object: {self.__class__.__name__}, Object ID: {object_id}, Deleted By User ID: {user.id if user else 'Anonymous'}")

