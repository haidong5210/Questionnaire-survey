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
            yield {"form":Question(),"id":None,"hide":"hide","option":""}

    return render(request, "que.html", {"form":inner()})


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