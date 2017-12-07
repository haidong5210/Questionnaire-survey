import json
from django.shortcuts import render,redirect,HttpResponse
from app01 import models
from django.forms import fields,Form,ModelForm
from django.forms import widgets as wd
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
                    models.Option.objects.filter(qs=qs_obj).delete()
                else:
                    models.Question.objects.filter(id=data_dict["id"]).update(title=data_dict["postion_title"],
                                                                              type=data_dict["type"],
                                                                              surveyInfo_id=nid)
                    for op_dict in data_dict["option"]:
                        models.Option.objects.create(name=op_dict['op_title'],
                                                     score=op_dict['op_score'],
                                                     qs=qs_obj)
            else:
                op_id_ser = models.Option.objects.filter(qs=qs_obj).values_list("id")
                op_l=[j[0] for j in op_id_ser]
                if data_dict['type'] == '1':
                    for opt_dict in data_dict['option']:
                        if 'op_id' in opt_dict:
                            op_l.remove(int(opt_dict['op_id']))
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