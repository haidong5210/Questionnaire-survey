from django.db import models

# Create your models here.


class User(models.Model):
    """
    员工表
    """
    username = models.CharField(max_length=32,verbose_name="用户名")
    password = models.CharField(max_length=32,verbose_name="密码")

    def __str__(self):
        return self.username


class ClassList(models.Model):
    """
    班级表
    """
    title = models.CharField(max_length=32,verbose_name="班级名")
    num = models.IntegerField(verbose_name="班级人数")

    def __str__(self):
        return self.title


class Student(models.Model):
    name = models.CharField(max_length=32,verbose_name="名字")
    password = models.CharField(max_length=32,verbose_name="密码")
    cls = models.ForeignKey(to=ClassList,verbose_name="所属班级",blank=True)

    def __str__(self):
        return self.name


class SurveyInfo(models.Model):
    """
    问卷表
    """
    title = models.CharField(max_length=32,verbose_name="问卷名")
    cls = models.ForeignKey(to=ClassList,verbose_name="问卷班级",blank=True)
    user = models.ForeignKey(to=User,verbose_name="创建者",blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    问题表
    """
    title = models.CharField(max_length=32,verbose_name="问题")
    type_list=(
        (1,"单选"),
        (2,"打分(1~10分)"),
        (3,"建议")
    )
    type=models.IntegerField(choices=type_list,verbose_name="类型")
    surveyInfo=models.ForeignKey(to=SurveyInfo,verbose_name="所属问卷",blank=True)

    def __str__(self):
        return self.name


class Option(models.Model):
    """
    单选题的选项
    """
    name = models.CharField(verbose_name='选项名称',max_length=32)
    score = models.IntegerField(verbose_name='选项对应的分值')
    qs = models.ForeignKey(to=Question)

    def __str__(self):
        return self.name


class Answer(models.Model):
    """
    答案表
    """
    student = models.ForeignKey(to=Student,verbose_name="某个学生",blank=True)
    question = models.ForeignKey(to=Question,verbose_name="某个问题",blank=True)
    score = models.CharField(max_length=32,null=True,verbose_name="分数")
    content = models.TextField(null=True,verbose_name="内容")
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")

    def __str__(self):
        return self.content