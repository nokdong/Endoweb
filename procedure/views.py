import time
from datetime import date

from procedure.models import Exam
from django import forms

from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy

from django.views.generic.edit import FormView
from procedure.forms import ProcedureSearchForm
from django.db.models import Q
from django.shortcuts import render

from django.views.generic.base import TemplateView

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import ColumnChart

class HomeView(TemplateView):
    template_name="home.html"

class UserCreateView(CreateView):
    template_name='registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register_done')

class UserCreateDoneTV(TemplateView):
    template_name = 'registration/register_done.html'

class ExamModelForm(forms.ModelForm):
    class Meta:
        model=Exam
        fields=['exam_date','exam_type','exam_doc', 'exam_class', 'exam_place','patient_name','hospital_no','patient_sex','patient_birth',
            'patient_phone','exam_Dx','exam_procedure','Bx_result','follow_up']
        widgets={'exam_type':forms.CheckboxSelectMultiple}
        widgets={'exam_procedure':forms.CheckboxSelectMultiple}

class ExamCreateView(CreateView):
    form_class = ExamModelForm
    model=Exam
    success_url = reverse_lazy("procedure:add")

    def form_valid(self, form):
        return super(ExamCreateView, self).form_valid(form)


class ProcedureFormView(FormView):
    form_class = ProcedureSearchForm
    template_name='procedure/post_search.html'

    def form_valid(self, form):
        schword='%s' % self.request.POST['search_word']
        post_list=Exam.objects.filter(Q(patient_name__icontains=schword) |
                                      Q(hospital_no__icontains=schword)).distinct()
        context={}
        context['form']=form
        context['search_term']=schword
        context['object_list']=post_list
        print (context)

        return render(self.request, self.template_name, context)



class BxUpdateview(UpdateView):
    model=Exam
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','follow_up']
    success_url = reverse_lazy('procedure:biopsy')

class BxListView(ListView):
    template_name = 'procedure/Bx_list.html'
    context_object_name='object_list'

    def get_queryset(self):
        result=Exam.objects.filter(Q(exam_procedure__icontains='Bx') |
                                   Q(exam_procedure__icontains='Polypectomy')|
                                   Q(exam_procedure__icontains='EMR')).distinct()
        return result

def add_month(date, months):
    month=date.month + int(months)-1
    year=int(date.year + (month/12))
    month=(month%12)+1
    day=date.day
    new_date=date.replace(year=year, month=month, day=day)
    return new_date

class PhoneListView(ListView):
    template_name='procedure/phone_list.html'
    context_object_name = 'object_list'

    today=date.today()

    def get_queryset(self):
        result=Exam.objects.filter(Q())

def phone(request):
    today=date.today()
    all_patients=Exam.objects.all()
    context={'object_list':[]}
    for patient in all_patients:
        call_date=add_month(patient.exam_date, patient.follow_up)
        if today.year==call_date.year and today.month==call_date.month:
            context['object_list'].append(patient)
    return render(request, 'procedure/phone_list.html', context)

class PhoneCheck(UpdateView):
    model=Exam
    template_name = 'procedure/phone_check.html'
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','phone_check']
    success_url = reverse_lazy('procedure:phone')

def today(request):
    today=date.today()
    g_egd = 0  # 건진위내시경
    j_egd = 0  # 진료위내시경
    g_colon = 0  # 건진대장내시경
    j_colon = 0  # 진료대장내시경
    sig = 0

    all_patients=Exam.objects.all()
    context={'object_list':[],'g_egd':0, 'j_egd':0, 'total_egd':0, 'g_colon':0, 'j_colon':0, 'total_colon':0, 'sig':0}
    for patient in all_patients:
        if patient.exam_date==today:
            context['object_list'].append(patient)
            if 'E' in patient.exam_type:
                if patient.exam_class =='건진':
                    g_egd+=1
                elif patient.exam_class=="진료":
                    j_egd+=1
            if 'C' in patient.exam_type:
                if patient.exam_class=="건진":
                    g_colon+=1
                elif patient.exam_class=="진료":
                    j_colon+=1
            if 'S' in patient.exam_type : sig+=1
    context['g_egd'] = g_egd
    context['j_egd'] = j_egd
    context['total_egd'] = g_egd + j_egd
    context['g_colon'] = g_colon
    context['j_colon'] = j_colon
    context['total_colon'] = g_colon + j_colon
    context['sig']=sig
    return render(request, 'procedure/today_list.html', context)

def thismonth(request):
    g_egd=0 #건진위내시경
    j_egd=0 #진료위내시경
    g_colon=0 #건진대장내시경
    j_colon=0 #진료대장내시경
    sig=0
    first_colon=0
    second_colon=0
    first_adenoma=0
    second_adenoma=0
    today=date.today()
    this_month=today.month
    this_year=today.year
    all_patients=Exam.objects.all()
    context={'object_list':[],'g_egd':0, 'j_egd':0, 'total_egd':0, 'g_colon':0, 'j_colon':0, 'total_colon':0, 'sig':0, 'first_colon':0, 'first_adr':0, 'second_colon':0, 'second_adr':0}
    for patient in all_patients:
        if patient.exam_date.year==this_year and patient.exam_date.month==this_month:
            context['object_list'].append(patient)
            if 'E' in patient.exam_type:
                if patient.exam_class =='건진':
                    g_egd+=1
                elif patient.exam_class=="진료":
                    j_egd+=1
            if 'C' in patient.exam_type:
                if patient.exam_doc=="이영재":
                    first_colon+=1
                elif patient.exam_doc=="김신일":
                    second_colon+=1

                if patient.exam_class=="건진":
                    g_colon+=1
                elif patient.exam_class=="진료":
                    j_colon+=1
            if 'S' in patient.exam_type : sig+=1
            if patient.exam_doc=="이영재" and 'adenoma' in patient.Bx_result:
                first_adenoma+=1
            if patient.exam_doc=="김신일" and 'adenoma' in patient.Bx_result:
                second_adenoma+=1
    context['g_egd']=g_egd
    context['j_egd'] = j_egd
    context['total_egd']=g_egd+j_egd
    context['g_colon']=g_colon
    context['j_colon']=j_colon
    context['total_colon']=g_colon+j_colon
    context['sig']=sig
    context['first_colon']=first_colon
    context['second_colon']=second_colon
    if first_colon !=0:
        context['first_adr']=int(float(first_adenoma)/first_colon *100)
    else : context['first_adr']='None'
    if second_colon !=0:
        context['second_adr'] = int(float(second_adenoma) / second_colon * 100)
    else : context['second_adr']='None'

    return render(request, 'procedure/this_month_list.html', context)


def year_data():
    today=date.today()
    today_year=today.year
    today_month=today.month
    egd=0
    colon=0
    all_patients = Exam.objects.all()
    data=[
        ['달','위내시경','대장내시경'],
    ]

    monthly_number={}
    for month in range(1, today_month+1):
        monthly_number[month]=[0,0]

    for patient in all_patients:
        patient_year=patient.exam_date.year
        patient_month=patient.exam_date.month
        for month in range(1,today_month+1):
            if patient_year==today_year and patient_month==month:
                if 'E' in patient.exam_type:
                    monthly_number[month][0]+=1
                if 'C' in patient.exam_type:
                    monthly_number[month][1] += 1

    for month in monthly_number:
         data.append([str(month), monthly_number[month][0], monthly_number[month][1]])
    return data


def graph(request):
    data=year_data()
    data_source = SimpleDataSource(data=data)
    chart = ColumnChart(data_source, options={'title': "올해 내시경 추이"})
    context = {'chart': chart}
    return render(request, 'procedure/year_graph.html', context)

"""
def graph(request):
    data=year_data()
    #data_source = SimpleDataSource(data=data)
    print (data)
    #chart = ColumnChart(data_source, options={'title': "올해 내시경 추이"})
    context = {'data': data}
    return render(request, 'procedure/year_graph.html', context)
"""