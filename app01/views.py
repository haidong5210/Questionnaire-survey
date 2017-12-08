import json
from django.shortcuts import render,redirect,HttpResponse
from app01 import models
from django.forms import fields,Form,ModelForm
from django.forms import widgets as wd
from django.core.exceptions import ValidationError
# Create your views here.


class Question(ModelForm):
    class Meta:
        model = models.Question
        fields = ["title","type"]
        widgets = {
            'title': wd.Textarea(attrs={"cols":"60","rows":"3"})
        }


class Option(ModelForm):
    class Meta:
        model = models.Option
        fields = ["name","score"]


def index(request):
    surveyinfo_list = models.SurveyInfo.objects.all()
    return render(request,"index.html",{"surveyinfo_list":surveyinfo_list})


# def questions(request,nid):
#     type_list = (
#         (1, "单选"),
#         (2, "打分(1~10分)"),
#         (3, "建议")
#     )
#     option_list = models.Option.objects.filter(qs__surveyInfo_id=nid)
#     question_list = models.Question.objects.filter(surveyInfo_id=nid)
#     # question_list1 = models.Question.objects.filter(surveyInfo_id=nid).values("name","type")
#
#     # class Inner:
#     #     def __iter__(self):
#     #         for i in question_list1:
#     #             yield Question(initial={"name":i["name"],"type":i["type"]})
#
#     return render(request,"questions.html",{"question_list":question_list,"type_list":type_list,"option_list":option_list})


def questions(request,nid):
    def inner():
        question_list = models.Question.objects.filter(surveyInfo_id=nid)
        if question_list:
            for question_obj in question_list:
                if question_obj.type == 1:
                    def op(que):
                        option_list = models.Option.objects.filter(qs=que)
                        for option_obj in option_list:
                            yield {"option":Option(instance=option_obj),"option_id":option_obj.id}
                    option = op(question_obj)
                    yield {"form": Question(instance=question_obj), "id": question_obj.id,"hide":"","option":option}
                else:
                    yield {"form":Question(instance=question_obj),"id":question_obj.id,"hide":"hide","option":""}
        else:
            yield {"form":Question(),"id":"","hide":"hide","option":""}

    return render(request, "que.html", {"form":inner(),"nid":nid})


def add(request):
    if request.method=="POST":
        surveyInfo = request.POST.get("surveyInfo")
        cls_id = request.POST.get("cla")
        user_id = request.POST.get("user")
        models.SurveyInfo.objects.create(title=surveyInfo,cls_id=cls_id,user_id=user_id)
        return redirect("/")
    user_list = models.User.objects.all()
    cls_list = models.ClassList.objects.all()
    return render(request,"add.html",{"user_list":user_list,"cls_list":cls_list})


def dell(request):
    surveyinfoId = request.GET.get("surveyinfoId")
    models.SurveyInfo.objects.filter(id=surveyinfoId).delete()
    return HttpResponse(1)


def data(request,nid):
    question_list = json.loads(request.POST.get("dt"))
    id_set = models.Question.objects.filter(surveyInfo_id=nid).values_list("id")
    l = [i[0] for i in id_set]
    for data_dict in question_list:
        if "id" in data_dict:  #之前存在的问题，但不一定没修改
            l.remove(int(data_dict['id']))           #把前端里删除的项 数据库也删掉
            qs_obj = models.Question.objects.filter(id=data_dict["id"])[0]  # 当前问题对象
            question_obj = models.Question.objects.filter(title=data_dict["postion_title"],   #是否数据库中存在当前问题
                                                          type=data_dict["type"],
                                                          surveyInfo_id=nid).first()
            if not question_obj:
                if not data_dict["type"] == '1':
                    models.Question.objects.filter(id=data_dict["id"]).update(title=data_dict["postion_title"],
                                                          type=data_dict["type"],
                                                          surveyInfo_id=nid)
                    models.Option.objects.filter(qs=qs_obj).delete()   #把之前type是1的项的option删除
                else:   #type为单选时的
                    models.Question.objects.filter(id=data_dict["id"]).update(title=data_dict["postion_title"],
                                                                              type=data_dict["type"],
                                                                              surveyInfo_id=nid)
                    for op_dict in data_dict["option"]:
                        models.Option.objects.create(name=op_dict['op_title'],
                                                     score=op_dict['op_score'],
                                                     qs=qs_obj)
            else:       #数据库中存在这个项  只对type是单选时做判断
                op_id_ser = models.Option.objects.filter(qs=qs_obj).values_list("id")
                op_l=[j[0] for j in op_id_ser]
                if data_dict['type'] == '1':
                    for opt_dict in data_dict['option']:
                        if 'op_id' in opt_dict:
                            op_l.remove(int(opt_dict['op_id']))           #前端中移除的option数据库也移除
                            option_set = models.Option.objects.filter(id=opt_dict["op_id"],name=opt_dict['op_title'],
                                                         score=opt_dict['op_score'],qs=qs_obj)
                            if not option_set:
                                models.Option.objects.filter(qs=qs_obj).update(name=opt_dict['op_title'],
                                                                               score=opt_dict['op_score'])
                        else:
                            models.Option.objects.create(name=opt_dict['op_title'],score=opt_dict['op_score'],qs=qs_obj)
                    if op_l:
                        for g in op_l:
                            models.Option.objects.filter(id=g).delete()
        else:
            if not "option" in data_dict:
                models.Question.objects.create(title=data_dict['postion_title'],type=data_dict['type'],
                                               surveyInfo_id=nid)
            else:
                ques_obj = models.Question.objects.create(title=data_dict['postion_title'], type=data_dict['type'],
                                               surveyInfo_id=nid)
                for opti_dict in data_dict['option']:
                    models.Option.objects.create(name=opti_dict["op_title"],score=opti_dict["op_score"],qs=ques_obj)
    if l:
        for k in l:
            models.Question.objects.filter(id=k).delete()
    return HttpResponse(json.dumps(True))


def login(request):
    if request.is_ajax():
        user = request.POST.get("user")
        pwd = request.POST.get("password")
        stu_obj = models.Student.objects.filter(name=user,password=pwd).first()
        login = {"log":False}
        if stu_obj:
            login['log'] = True
            request.session['user']={"password":stu_obj.password,"name":stu_obj.name,"id":stu_obj.id}
        return HttpResponse(json.dumps(login))
    else:
        return render(request,"login.html")


def func(val):
    if len(val) < 15:
        raise ValidationError("你太短了！！")


def answer(request,sur_id,cls_id):
    if not request.session.get("user"):
        return redirect("/login/")
    else:
        #不是此次答题班级的学生
        stud_list = models.Student.objects.filter(cls_id=cls_id,name=request.session["user"]["name"],password=request.session["user"]["password"])
        if not stud_list:
            return HttpResponse("你不是此次答题班级的学生，是不是想串班！！！")
        #答过题的学生，不能再次答！！
        answer_list = models.Answer.objects.filter(student_id=request.session["user"]["id"],question__surveyInfo_id=sur_id)
        if answer_list:
            return HttpResponse("你已经答过此次问卷，谢谢您的参与！！")
        #form组件#另一种生成form组件的形式，对象也是用type生成的
        question_list = models.Question.objects.filter(surveyInfo_id=sur_id)
        questions_dict = {}
        for question_obj in question_list:
            if question_obj.type == 1:
                questions_dict["option_id_%s"%question_obj.id]=fields.ChoiceField(label=question_obj.title,
                                                                                  choices=models.Option.objects.filter(qs_id=question_obj.id).values_list("id","score"),
                                                                        widget=wd.RadioSelect,
                                                                        error_messages={"required":"内容不能为空！"})
            elif question_obj.type == 2:
                questions_dict["score_%s"%question_obj.id]=fields.ChoiceField(label=question_obj.title,
                                                                              choices=[(i,i) for i in range(1,11)],
                                                                      widget=wd.RadioSelect,
                                                                      error_messages={"required": "内容不能为空！"})
            else:
                questions_dict["content_%s"%question_obj.id]=fields.CharField(label=question_obj.title,
                                                                              widget=wd.Textarea,
                                                                      error_messages={"required": "内容不能为空！"},
                                                                              validators=[func,])
        TestQuestion = type("Test", (Form,),questions_dict)
        if request.method == "GET":
            form = TestQuestion()
            return render(request,"answer.html",{"form":form})
        else:
            form = TestQuestion(request.POST)
            if not form.is_valid():
                return render(request, "answer.html", {"form": form})
            else:
                answer_l = []
                for key,v in form.cleaned_data.items():  #{'content_1': 'asdasdasdasdasdasdasdasdasd', 'score_2': '3', 'option_id_3': '8'}
                    field,ques_id = key.rsplit("_",1)
                    answer_dict = {'student_id':request.session["user"]["id"],"question_id":ques_id,field:v}
                    answer_l.append(models.Answer(**answer_dict))
                models.Answer.objects.bulk_create(answer_l)
                return HttpResponse("感谢您的参与！！我们献上诚挚的感谢")