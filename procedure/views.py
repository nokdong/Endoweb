from datetime import date

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from graphos.renderers.gchart import ColumnChart
from graphos.sources.simple import SimpleDataSource

from endo.views import LoginRequiredMixin
from procedure.forms import ProcedureSearchForm
from procedure.models import Exam


class HomeView(TemplateView):
    template_name="home.html"


class ExamModelForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model=Exam
        fields=['exam_date','exam_type','exam_doc', 'exam_class', 'exam_place','patient_name','hospital_no','patient_sex','patient_birth',
            'patient_phone','exam_Dx','exam_procedure','Bx_result','follow_up']
        widgets={'exam_type':forms.CheckboxSelectMultiple}
        widgets={'exam_procedure':forms.CheckboxSelectMultiple}

class ExamCreateView(LoginRequiredMixin, CreateView):
    form_class = ExamModelForm
    model=Exam
    success_url = reverse_lazy("procedure:add")

    def form_valid(self, form):
        return super(ExamCreateView, self).form_valid(form)


class ProcedureFormView(LoginRequiredMixin, FormView):
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



class BxUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','follow_up']
    success_url = reverse_lazy('procedure:biopsy')

class TodayUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','follow_up']
    success_url = reverse_lazy('procedure:today')

class MonthUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','follow_up']
    success_url = reverse_lazy('procedure:thismonth')

class BxListView(LoginRequiredMixin, ListView):
    template_name = 'procedure/Bx_list.html'
    context_object_name='object_list'

    def get_queryset(self):
        result=Exam.objects.filter(Q(exam_procedure__icontains='Bx') |
                                   Q(exam_procedure__icontains='Polypectomy')|
                                   Q(exam_procedure__icontains='EMR')).distinct()
        return result

class ReadingUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','follow_up']
    success_url = reverse_lazy('procedure:readinglist')

class ReadingListView(LoginRequiredMixin, ListView):
    template_name = 'procedure/reading_list.html'
    context_object_name='object_list'

    def get_queryset(self):
        result=Exam.objects.filter(exam_Dx ='.')
        return result

def add_month(date, months):
    month=date.month + int(months)-1
    year=int(date.year + (month/12))
    month=(month%12)+1
    day=date.day
    new_date=date.replace(year=year, month=month, day=1)
    return new_date


@login_required
def phone(request):
    today=date.today()
    all_patients=Exam.objects.all()
    print (all_patients)

    context={'phone_list':[], 'phoned_list':[], 'visited_list':[],  'total_number':0, 'will_phone_number':0, 'phoned_number':0, 'visited_number':0, 'phoned_fraction':0,"visited_fraction":0}
    for patient in all_patients:
        call_date=add_month(patient.exam_date, patient.follow_up)
        if today.year==call_date.year and today.month==call_date.month :
            if patient.exam_date.year == today.year and patient.exam_date.month == today.month:
                continue;
            else:
                if patient.phone_check == '.':
                    context['phone_list'].append(patient)
                elif patient.phone_check !='.':
                    if patient.re_visit == True:
                        context['visited_list'].append(patient)
                    else :
                        context['phoned_list'].append(patient)

    context['will_phone_number']=len(context['phone_list'])
    context['visited_number'] = len(context['visited_list'])
    context['phoned_number']=len(context['phoned_list'])+context['visited_number']
    context['total_number'] = context['will_phone_number'] + context['phoned_number']
    if context['total_number'] ==0:
        context['phoned_fraction'], context['visited_fraction'] = 0,0
    else :
        context['phoned_fraction']=round(float(context['phoned_number'])/context['total_number']*100)
        context['visited_fraction']=round(float(context['visited_number'])/context['total_number']*100)

    return render(request, 'procedure/phone_list.html', context)

class PhoneCheck(LoginRequiredMixin, UpdateView):
    model=Exam
    template_name = 'procedure/phone_check.html'
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','phone_check', 'follow_up']
    success_url = reverse_lazy('procedure:phone')

class ReVisit(LoginRequiredMixin, UpdateView):
    model=Exam
    template_name = 'procedure/re_visit.html'
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','phone_check','re_visit']
    success_url = reverse_lazy('procedure:phone')

@login_required
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

@login_required
def thismonth(request):
    g_egd=0 #건진위내시경
    j_egd=0 #진료위내시경
    g_colon=0 #건진대장내시경
    j_colon=0 #진료대장내시경
    sig=0
    first_colon=0
    second_colon=0
    first_polyp=0
    second_polyp=0
    first_adenoma=0
    second_adenoma=0
    today=date.today()
    this_month=today.month
    this_year=today.year
    all_patients=Exam.objects.all()
    context={'object_list':[],'g_egd':0, 'j_egd':0, 'total_egd':0, 'g_colon':0, 'j_colon':0, 'total_colon':0, 'sig':0, 'first_colon':0,
             'first_polyp_rate':0, 'first_adr':0, 'second_colon':0, 'second_polyp_rate':0, 'second_adr':0}
    for patient in all_patients:
        if patient.exam_date.year==this_year and patient.exam_date.month==this_month:
            context['object_list'].append(patient)
            if 'E' in patient.exam_type:
                if patient.exam_class =='건진':
                    g_egd+=1
                elif patient.exam_class=="진료":
                    j_egd+=1
                elif patient.exam_class == "건진+진료":
                    g_egd+=1

            if 'C' in patient.exam_type:
                if patient.exam_doc=="이영재":
                    first_colon+=1
                    if 'Polypectomy' in patient.exam_procedure or 'EMR' in patient.exam_procedure:
                        first_polyp+=1
                    if 'adenoa' in patient.Bx_result:
                        first_adenoma+=1
                elif patient.exam_doc=="김신일":
                    second_colon+=1
                    if 'Polypectomy' in patient.exam_procedure or 'EMR' in patient.exam_procedure:
                        second_polyp+=1
                    if 'adenoma' in patient.Bx_result:
                        second_adenoma+=1

                if patient.exam_class=="건진":
                    g_colon+=1
                elif patient.exam_class=="진료":
                    j_colon+=1
                elif patient.exam_class=="건진+진료":
                    j_colon+=1



            if 'S' in patient.exam_type : sig+=1

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
        context['first_polyp_rate']=int(float(first_polyp)/first_colon *100)
        context['first_adr'] = int(float(first_adenoma) / first_colon * 100)
    else : context['first_polyp_rate']='None'
    if second_colon !=0:
        context['second_polyp_rate'] = int(float(second_polyp) / second_colon * 100)
        context['second_adr'] = int(float(second_adenoma) / second_colon * 100)
    else : context['second_polyp_rate']='None'

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

@login_required
def graph(request):
    data=year_data()
    data_source = SimpleDataSource(data=data)
    chart = ColumnChart(data_source, options={'title': "올해 내시경 추이"})
    context = {'chart': chart}
    return render(request, 'procedure/year_graph.html', context)


