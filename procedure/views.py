from datetime import date, datetime
import collections
import sys

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView


from endo.views import LoginRequiredMixin
from procedure.forms import ProcedureSearchForm, DurationStaticForm
from procedure.models import Exam
from bokeh.plotting import figure, save, output_file, ColumnDataSource
from bokeh.layouts import column
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import Legend, HoverTool

request_token = None

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

def post_update_search(request):
    template_name = 'procedure/post_search.html'
    return render(request, template_name, request_token)




class ProcedureFormView(LoginRequiredMixin, FormView):
    form_class = ProcedureSearchForm
    template_name='procedure/post_search.html'

    def form_valid(self, form):
        global request_token
        print (self.request.POST)
        schword='%s' % self.request.POST['search_word']
        first_date='%s' % self.request.POST['first_date']
        last_date = '%s' % self.request.POST['last_date']
        #first_date = self.request.POST['first_date_year']+'-'+self.request.POST['first_date_month']+'-'+self.request.POST['first_date_day']
        #last_date = self.request.POST['last_date_year'] + '-' + self.request.POST['last_date_month'] + '-' + self.request.POST['last_date_day']
        if first_date =='' and last_date == '':
            post_list = Exam.objects.filter(Q(patient_name__icontains=schword) | Q(hospital_no=schword) | Q(exam_Dx__icontains=schword) |
                                            Q(Bx_result__icontains = schword)).distinct()
            patient_number=len(post_list)
        elif first_date is not '0-0-0' and last_date is not '0-0-0':
            post_list=Exam.objects.filter((Q(exam_date__gte=first_date) & Q(exam_date__lte=last_date)) & (Q(patient_name__icontains=schword) |
                                      Q(hospital_no=schword) | Q(exam_Dx__icontains=schword) | Q(Bx_result__icontains=schword))).distinct()
            patient_number = len(post_list)
        context={}
        context['form']=form
        context['search_term']=schword
        context['object_list']=post_list
        context['patient_number']=patient_number
        #context['request']=str(self.request.POST)
        request_token = context

        return render(self.request, self.template_name, context)


# class DurationStatic(LoginRequiredMixin, FormView):
#     form_class = DurationStaticForm
#     template_name = 'procedure/duration_static.html'
#
#     def form_valid(self, form):
#         first_date=self.request.POST['first_date']
#         last_date=self.request.POST['last_date']
#
#         context={}
#         object_list=Exam.objects.filter(Q(exam_date__gte=first_date) & Q(exam_date__lte=last_date))
#         object_list.order_by('exam_date')
#         context['form'] = form
#         context['object_list']=object_list
#
#
#         return render(self.request, self.template_name, context)




class BxUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    template_name = 'procedure/Bx_update.html'
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result', 'Bx_result_call', 'follow_up']
    success_url = reverse_lazy('procedure:biopsy')

class BxCallUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    template_name = 'procedure/Bx_update.html'
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result', 'Bx_result_call', 'follow_up']
    success_url = reverse_lazy('procedure:Bx_call')
'''
@login_required
def search_update_func(request, pk, q):
    patient=Exam.objects.get(id=pk)
    print (patient.exam_date)

    return
'''
class SearchUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result', 'Bx_result_call','follow_up',
              'phone_check','re_visit']
    template_name = 'procedure/post_search_update.html'
    success_url = reverse_lazy('procedure:post_update_search')

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

class BxCallView(LoginRequiredMixin, ListView):
    template_name = 'procedure/Bx_call.html'
    context_object_name='object_list'

    def get_queryset(self):
        result=Exam.objects.filter(Q(exam_date__gte = date(2017, 2, 27)) &
                                                      (Q(exam_procedure__icontains='Bx') |
                                   Q(exam_procedure__icontains='Polypectomy')|
                                   Q(exam_procedure__icontains='EMR'))).distinct()
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
                elif patient.exam_class == "건진+진료":
                    g_egd+=1
            if 'C' in patient.exam_type:
                if patient.exam_class=="건진":
                    g_colon+=1
                elif patient.exam_class=="진료":
                    j_colon+=1
                elif patient.exam_class == "건진+진료":
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

    monthly_data = Exam.objects.filter(exam_date__year=this_year).filter(exam_date__month=this_month)
    g_egd = monthly_data.filter(exam_type__contains='E').filter(exam_class__contains="건진").count()
    j_egd = monthly_data.filter(exam_type__contains = 'E').filter(exam_class__contains="진료").exclude(exam_class = "건진+진료").count()
    g_colon = monthly_data.filter(exam_type__contains='C').filter(exam_class__contains="건진").exclude(exam_class = "건진+진료").count()
    j_colon = monthly_data.filter(exam_type__contains='C').filter(exam_class__contains="진료").count()
    sig = monthly_data.filter(exam_type__contains='S').count()
    first_colon=monthly_data.filter(exam_doc = '이영재').filter(exam_type__contains='C').count()
    second_colon=monthly_data.filter(exam_doc = '김신일').filter(exam_type__contains='C').count()
    first_polyp=monthly_data.filter(exam_doc = '이영재').filter(exam_type__contains='C').filter(exam_Dx__contains = 'polyp').count()
    second_polyp = monthly_data.filter(exam_doc='김신일').filter(exam_type__contains='C').filter(
        exam_Dx__contains='polyp').count()
    first_adenoma = monthly_data.filter(exam_doc = '이영재').filter(exam_type__contains='C').filter(Bx_result__contains = 'adenoma').count()
    second_adenoma = monthly_data.filter(exam_doc='김신일').filter(exam_type__contains='C').filter(Bx_result__contains='adenoma').count()


    context={'object_list':[],'g_egd':0, 'j_egd':0, 'total_egd':0, 'g_colon':0, 'j_colon':0, 'total_colon':0, 'sig':0, 'first_colon':0,
             'first_polyp_rate':0, 'first_adr':0, 'second_colon':0, 'second_polyp_rate':0, 'second_adr':0,
             'total_polyp_rate':0, 'total_adenoma_rate':0}

    context['object_list'] = monthly_data
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
    else : context['first_polyp_rate']='0'
    if second_colon !=0:
        context['second_polyp_rate'] = int(float(second_polyp) / second_colon * 100)
        context['second_adr'] = int(float(second_adenoma) / second_colon * 100)
    else : context['second_polyp_rate']='0'

    if context['total_colon']!=0:
        context['total_polyp_rate'] = int(float(first_polyp + second_polyp) / context['total_colon'] * 100)
        context['total_adenoma_rate'] = int(float(first_adenoma + second_adenoma) / context['total_colon'] * 100)
    else:
        context['total_polyp_rate'],context['total_adenoma_rate']='0','0'

    return render(request, 'procedure/this_month_list.html', context)

def re_visited(current_year, current_month, objects):
    visited=0
    call=0
    for patient in objects:
        follow_up_date=add_month(patient.exam_date, patient.follow_up)
        if follow_up_date.year == current_year and follow_up_date.month==current_month and patient.follow_up != 0:
            call+=1
            if patient.re_visit == True:
                visited+=1
    return int(float(visited) / call*100)

def thisyear(request):
    this_month = date.today().month

    g_egd = 0  # 건진위내시경
    j_egd = 0  # 진료위내시경
    g_colon = 0  # 건진대장내시경
    j_colon = 0  # 진료대장내시경
    sig = 0
    first_colon = 0
    second_colon = 0
    first_polyp = 0
    second_polyp = 0
    first_adenoma = 0
    second_adenoma = 0
    total_sum_re_visit=0
    today = date.today()
    this_month = today.month
    this_year = today.year

    monthly_total_data=collections.OrderedDict()
    until_now_total = {'until_now_total_egd':0, 'until_now_g_egd':0, 'until_now_j_egd':0,
                       'until_now_first_colon':0, 'until_now_second_colon':0, 'until_now_g_colon':0, 'until_now_j_colon':0, 'until_now_total_colon':0,
                       'until_now_total_colon_including_sig':0,
                       'until_now_first_polyp':0, 'until_now_second_polyp':0,
                       'until_now_average_first_pdr':0, 'until_now_average_second_pdr':0, 'until_now_total_average_pdr':0,
                       'until_now_first_adenoma':0, 'until_now_second_adenoma':0,
                       'until_now_average_first_adr':0, 'until_now_second_adr':0, 'until_now_total_average_adr':0,
                       'until_now_PEG':0, 'until_now_re_visit':0}

    for month in range(1, this_month+1):
        context = {'g_egd': 0, 'j_egd': 0, 'total_egd': 0, 'g_colon': 0, 'j_colon': 0, 'total_colon': 0,
                   'sig': 0, 'sig_included_toal_colon':0, 'j_colon_including_sig':0,
                   'first_colon': 0, 'first_polyp_rate': 0, 'first_adr': 0,
                   'second_colon': 0, 'second_polyp_rate': 0, 'second_adr': 0,
                   'total_polyp_rate': 0, 'total_adenoma_rate': 0, 'PEG':0, 're_visit':0}

        monthly_data = Exam.objects.filter(exam_date__year=this_year).filter(exam_date__month=month)
        g_egd = monthly_data.filter(exam_type__contains='E').filter(exam_class__contains="건진").count()
        j_egd = monthly_data.filter(exam_type__contains='E').filter(exam_class__contains="진료").exclude(
            exam_class="건진+진료").count()
        g_colon = monthly_data.filter(exam_type__contains='C').filter(exam_class__contains="건진").exclude(
            exam_class="건진+진료").count()
        j_colon = monthly_data.filter(exam_type__contains='C').filter(exam_class__contains="진료").count()
        sig = monthly_data.filter(exam_type__contains='S').count()
        first_colon = monthly_data.filter(exam_doc='이영재').filter(exam_type__contains='C').count()
        second_colon = monthly_data.filter(exam_doc='김신일').filter(exam_type__contains='C').count()
        first_polyp = monthly_data.filter(exam_doc='이영재').filter(exam_type__contains='C').filter(
            exam_Dx__contains='polyp').count()
        second_polyp = monthly_data.filter(exam_doc='김신일').filter(exam_type__contains='C').filter(
            exam_Dx__contains='polyp').count()
        first_adenoma = monthly_data.filter(exam_doc='이영재').filter(exam_type__contains='C').filter(
            Bx_result__contains='adenoma').count()
        second_adenoma = monthly_data.filter(exam_doc='김신일').filter(exam_type__contains='C').filter(
            Bx_result__contains='adenoma').count()
        PEG = monthly_data.filter(exam_procedure=['PEG']).count()


        context['g_egd'] = g_egd
        context['j_egd'] = j_egd
        context['total_egd'] = g_egd + j_egd
        until_now_total['until_now_g_egd'] +=g_egd
        until_now_total['until_now_j_egd'] += j_egd
        until_now_total['until_now_total_egd'] += context['total_egd']

        context['g_colon'] = g_colon
        context['j_colon'] = j_colon
        context['total_colon'] = g_colon + j_colon
        until_now_total['until_now_g_colon']+=g_colon
        until_now_total['until_now_j_colon'] += j_colon+sig
        until_now_total['until_now_total_colon_including_sig'] += g_colon + j_colon + sig

        context['sig'] = sig
        context['sig_included_total_colon'] = g_colon + j_colon + sig
        context['j_colon_including_sig']=j_colon + sig
        context['first_colon'] = first_colon
        context['second_colon'] = second_colon

        context['PEG']=PEG
        until_now_total['until_now_PEG'] += PEG

        context['re_visit'] = re_visited(this_year, month, Exam.objects.all())
        total_sum_re_visit += context['re_visit']

        if first_colon != 0:
            until_now_total['until_now_first_colon'] += first_colon
            until_now_total['until_now_first_polyp'] += first_polyp
            context['first_polyp_rate'] = int(float(first_polyp) / first_colon * 100)
            until_now_total['until_now_first_adenoma'] +=first_adenoma
            context['first_adr'] = int(float(first_adenoma) / first_colon * 100)
        else:
            context['first_polyp_rate'] = '0'

        if second_colon != 0:
            until_now_total['until_now_second_colon']+= second_colon
            until_now_total['until_now_second_polyp'] += second_polyp
            context['second_polyp_rate'] = int(float(second_polyp) / second_colon * 100)
            until_now_total['until_now_second_adenoma'] += second_adenoma
            context['second_adr'] = int(float(second_adenoma) / second_colon * 100)
        else:
            context['second_polyp_rate'] = '0'

        if context['total_colon'] != 0:
            context['total_polyp_rate'] = int(float(first_polyp + second_polyp) / context['total_colon'] * 100)
            context['total_adenoma_rate'] = int(float(first_adenoma + second_adenoma) / context['total_colon'] * 100)
        else:
            context['total_polyp_rate'], context['total_adenoma_rate'] = '0', '0'

        monthly_total_data[str(month)] = context

    until_now_total['until_now_total_colon']=until_now_total['until_now_first_colon']+until_now_total['until_now_second_colon']
    until_now_total['until_now_average_first_pdr'] = int(float(until_now_total['until_now_first_polyp']) /
                                                          until_now_total['until_now_first_colon'] *100)
    until_now_total['until_now_average_second_pdr'] = int(float(until_now_total['until_now_second_polyp']) /
                                                          until_now_total['until_now_second_colon'] * 100)
    until_now_total['until_now_total_average_pdr'] = int(float(until_now_total['until_now_first_polyp']+until_now_total['until_now_second_polyp']) / until_now_total['until_now_total_colon']*100)
    until_now_total['until_now_average_first_adr'] = int(float(until_now_total['until_now_first_adenoma']) /
                                                         until_now_total['until_now_first_colon'] * 100)
    until_now_total['until_now_average_second_adr'] = int(float(until_now_total['until_now_second_adenoma']) /
                                                         until_now_total['until_now_second_colon'] * 100)
    until_now_total['until_now_total_average_adr'] = int(float(until_now_total['until_now_first_adenoma'] + until_now_total['until_now_second_adenoma']) / until_now_total[
            'until_now_total_colon'] * 100)
    until_now_total['until_now_re_visit'] = int(float(total_sum_re_visit) / len(monthly_total_data))
    return render(request, 'procedure/this_year_summary.html',{'monthly_total_data':monthly_total_data, 'until_now_total':until_now_total} )


def year_data(year):

    egd=0
    colon=0

    all_patients = Exam.objects.all()

    all_month = [1,2,3,4,5,6,7,8,9,10,11,12]
    monthly_egd= {1: 0,2: 0,3: 0,4: 0,5: 0,6: 0,7: 0,8: 0,9: 0,10: 0,11: 0,12: 0}
    monthly_colon = {1: 0,2: 0,3: 0,4: 0,5: 0,6: 0,7: 0,8: 0,9: 0,10: 0,11: 0,12: 0}

    for patient in all_patients:
        patient_year=patient.exam_date.year
        patient_month=patient.exam_date.month
        for month in range(1,13):
            if patient_year==year and patient_month==month:
                if 'E' in patient.exam_type:
                    monthly_egd[month]+=1
                if 'C' in patient.exam_type or 'S' in patient.exam_type:
                    monthly_colon[month] += 1

    return list(monthly_egd.values()), list(monthly_colon.values())

@login_required
def graph(request):
    data=year_data()
    data_source = SimpleDataSource(data=data)
    chart = ColumnChart(data_source, options={'title': "올해 내시경 추이"})
    context = {'chart': chart}
    return render(request, 'procedure/year_graph.html', context)

def homegraph(request):
    today = date.today()
    monthly_egd, monthly_colon = year_data(today.year)
    #total_months = [1,2,3,4,5,6,7,8,9,10,11,12]
    #egd_2015 = [436, 298, 155, 110, 54, 65, 67, 51, 61, 85, 114, 185]
    #colon_2015 =[19, 12, 29, 27, 11, 4, 19, 8, 10, 15, 19, 38]
    #egd_2016 = [291, 219, 102, 84, 65, 92, 73, 79, 70, 84, 123, 163]
    #colon_2016 = [20, 23, 40, 43, 30, 35, 28, 29, 17, 21, 29, 50]

    source = ColumnDataSource(
        data={'total_months':[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'egd_2015':[436, 298, 155, 110, 54, 65, 67, 51, 61, 85, 114, 185],
              'egd_2016':[291, 219, 102, 84, 65, 92, 73, 79, 70, 84, 123, 163],
              'egd_2017':[220,259,160,110,107,96,98,85,84,75,111,184], 'monthly_egd':monthly_egd,
              'colon_2015':[19, 12, 29, 27, 11, 4, 19, 8, 10, 15, 19, 38], 'colon_2016':[20, 23, 40, 43, 30, 35, 28, 29, 17, 21, 29, 50],
              'colon_2017':[25,48,40,18,30,29,39,31,28,23,51,33],
              'monthly_colon':monthly_colon})

    egd = figure(x_axis_type ='datetime', x_axis_label ='월', y_axis_label = '개수', width=1000, height=330,  tools=[], toolbar_location = "above")
    #egd.background_fill_color = 'LightCyan'
    e1=egd.vbar(x='total_months', width=0.5, bottom=0, top='monthly_egd', color='firebrick', alpha = 0.8, source=source)
    egd.add_tools(HoverTool(renderers = [e1], tooltips=[("개수", '@monthly_egd')]))
    e2=egd.circle('total_months','egd_2017', size = 10,  color='navy', source=source)
    egd.add_tools(HoverTool(renderers=[e2], tooltips=[("개수", '@egd_2017')]))
    e3=egd.circle('total_months', 'egd_2016', size=10, color='DarkCyan', source=source)
    egd.add_tools(HoverTool(renderers=[e3], tooltips=[("개수", '@egd_2016')]))
    e4=egd.circle('total_months', 'egd_2015', size=10, color='yellow', source=source)
    egd.add_tools(HoverTool(renderers=[e4], tooltips=[("개수", '@egd_2015')]))

    egd_tab = Panel(child = egd, title = "위내시경 추이")

    egd_legend = Legend(items = [
        ("2018년", [e1]),
        ("2017년", [e2]),
        ("2016년", [e3]),
        ("2015년",[e4]),], location = (0,-30))
    egd_legend.border_line_color = 'SkyBlue'
    egd_legend.border_line_width = 3
    egd.add_layout(egd_legend, 'right')

    colon = figure(x_axis_type ='datetime', x_axis_label ='월', y_axis_label = '개수', width = 1000, height=330, tools=[], toolbar_location = "above")
    c1=colon.vbar(x='total_months', width=0.5, bottom=0, top='monthly_colon', color='firebrick', alpha = 0.8, source=source)
    colon.add_tools(HoverTool(renderers=[c1], tooltips=[("개수", '@monthly_colon')]))
    c2 =colon.circle('total_months','colon_2017', size = 10,  color='navy', source=source)
    colon.add_tools(HoverTool(renderers=[c2], tooltips=[("개수", '@colon_2017')]))
    c3 =colon.circle('total_months', 'colon_2016', size=10,  color='DarkCyan', source=source)
    colon.add_tools(HoverTool(renderers=[c3], tooltips=[("개수", '@colon_2016')]))
    c4 = colon.circle('total_months', 'colon_2015', size=10, color='yellow', source=source)
    colon.add_tools(HoverTool(renderers=[c4], tooltips=[("개수", '@colon_2015')]))

    colon_legend = Legend(items=[("2018년", [c1]), ("2017년", [c2]), ("2016년", [c3]), ("2015년", [c4]), ], location=(0, -30))
    colon_legend.border_line_color = 'SkyBlue'
    colon_legend.border_line_width = 3
    colon.add_layout(colon_legend, 'right')

    colon_tab = Panel(child=colon, title = "대장내시경 추이")
    layout = Tabs(tabs = [egd_tab, colon_tab])

    if sys.platform.startswith('win32'):
        output_file('procedure/templates/procedure/vbar.html')
        save(layout)
        return render(request, 'procedure/vbar.html')
    else:
        output_file('/home/nokdong/Endoweb/procedure/templates/procedure/vbar.html')
        save(layout)
        return render(request, '/home/nokdong/Endoweb/procedure/templates/procedure/vbar.html')


'''
    data=year_data()
    data_source = SimpleDataSource(data=data)
    chart = ColumnChart(data_source, options={'title': "올해 내시경 추이"})
    context = {'chart': chart}
    return render(request, 'procedure/home_year_graph.html', context)

'''

def home(request):
    none_Bx = 0  # Bx 결과 안들어 간 사람
    Bx_call = 0 # Bx 결과 전화 통보 해 줘야 할 사람
    none_reading = 0  # 판독 안들어 간 사람
    will_phone = 0  # 전화해야할 사람

    today_g_egd, today_j_egd=0,0
    today_g_colon, today_j_colon=0,0
    today_sig=0

    month_g_egd, month_j_egd, month_total_egd = 0,0,0  # 이번달 건진위내시경, 진료위내시경
    month_g_colon, month_j_colon, month_total_colon = 0,0,0  # 이번달 건진대장내시경, 진료대장내시경
    month_sig = 0 # 이번달 직장내시경

    first_colon = 0 # 1내과대장
    second_colon = 0 # 2내과대장
    first_polyp = 0 # 1내과용종
    second_polyp = 0 # 2내과 용종
    first_adenoma = 0 #1내과 선종
    second_adenoma = 0 #2내과 선종
    first_polyp_rate=0
    second_polyp_rate=0
    first_adenoma_rate=0
    second_adenoma_rate=0
    total_polyp_rate, total_adenoma_rate=0,0


    today = date.today()
    this_month = today.month
    this_year = today.year

    temp_egd={}
    temp_colon={}
    for month in range(1,13):
        monthly_data = Exam.objects.filter(exam_date__year=2017).filter(exam_date__month=month)
        temp_egd[month]=monthly_data.filter(exam_type__contains='E').count()
        temp_colon[month]=monthly_data.filter(exam_type__contains='C').count() + monthly_data.filter(exam_type__contains='S').count()
    print (temp_egd)
    print (temp_colon)

    all_patients = Exam.objects.all()
    context = {'none_Bx': 0, 'Bx_call':0, 'none_reading': 0, 'will_phone': 0,
               'today_g_egd': today_g_egd, 'today_j_egd': today_j_egd,
               'today_g_colon': today_g_colon, 'today_j_colon': today_j_colon, 'today_sig': 0,
               'today_total_egd':0, 'today_total_colon':0,
               'month_g_egd': month_g_egd, 'month_j_egd': month_j_egd,
               'month_g_colon': month_g_colon, 'month_j_colon': month_j_colon, 'month_sig': 0,
               'month_total_egd':month_total_egd,
               'month_total_colon': month_total_colon,
               'first_colon': first_colon, 'second_colon': second_colon,
               'first_polyp_rate': first_polyp_rate, 'second_polyp_rate': second_polyp_rate,
               'first_adenoma_rate': first_adenoma_rate, 'second_adenoma_rate': second_adenoma_rate,
               'total_polyp_rate': total_polyp_rate, 'total_adenoma_rate': total_adenoma_rate}

    for patient in all_patients:
        if patient.exam_procedure in [['EMR'],['Polypectomy'],['Bx'], ['Bx', 'EMR'], ['Bx', 'Polypectomy'],['EMR','Polypectomy'],['Bx','EMR','Polypectomy']] and patient.Bx_result=='.':
            none_Bx+=1
    context['none_Bx']=none_Bx

    for patient in all_patients:
        if patient.exam_procedure in [['EMR'],['Polypectomy'],['Bx'], ['Bx', 'EMR'], ['Bx', 'Polypectomy'],['Polypectomy', 'EMR'],['Bx','Polypectomy','EMR'],['Bx','CLO'],['CLO'],['CLO','EMR'],['CLO','Polypectomy','EMR']] and patient.Bx_result_call =='.' and patient.exam_date >= date(2017, 2, 27):
            Bx_call+=1
    context['Bx_call']=Bx_call

    for patient in all_patients:
        if patient.exam_Dx=='.': none_reading+=1
    context['none_reading']=none_reading

    for patient in all_patients:
        call_date=add_month(patient.exam_date, patient.follow_up)
        if today.year==call_date.year and today.month==call_date.month:
            if patient.exam_date.year==today.year and patient.exam_date.month==today.month:
                continue;
            else :
                if patient.phone_check=='.' : will_phone+=1
    context['will_phone']=will_phone

    for patient in all_patients:
        if patient.exam_date == today:
            if 'E' in patient.exam_type:
                if patient.exam_class == '건진':
                    today_g_egd += 1
                elif patient.exam_class == "진료":
                    today_j_egd += 1
                elif patient.exam_class == "건진+진료":
                    today_g_egd += 1
            if 'C' in patient.exam_type:
                if patient.exam_class == "건진":
                    today_g_colon += 1
                elif patient.exam_class == "진료":
                    today_j_colon += 1
                elif patient.exam_class == "건진+진료":
                    today_j_colon += 1
            if 'S' in patient.exam_type: today_sig += 1
    context['today_g_egd'], context['today_j_egd'], context['today_g_colon'], context['today_j_colon']=today_g_egd, today_j_egd, today_g_colon, today_j_colon
    context['today_sig']=today_sig
    context['today_total_egd']=today_g_egd+today_j_egd
    context['today_total_colon']=today_g_colon+today_j_colon

    for patient in all_patients:
        if patient.exam_date.year == this_year and patient.exam_date.month == this_month:
            if 'E' in patient.exam_type:
                if patient.exam_class == '건진':
                    month_g_egd += 1
                elif patient.exam_class == "진료":
                    month_j_egd += 1
                elif patient.exam_class == "건진+진료":
                    month_g_egd += 1

            if 'C' in patient.exam_type:
                if patient.exam_doc == "이영재":
                    first_colon += 1
                    if 'Polypectomy' in patient.exam_procedure or 'EMR' in patient.exam_procedure:
                        first_polyp += 1
                    if 'adenoma' in patient.Bx_result:
                        first_adenoma += 1
                elif patient.exam_doc == "김신일":
                    second_colon += 1
                    if 'Polypectomy' in patient.exam_procedure or 'EMR' in patient.exam_procedure:
                        second_polyp += 1
                    if 'adenoma' in patient.Bx_result:
                        second_adenoma += 1

                if patient.exam_class == "건진":
                    month_g_colon += 1
                elif patient.exam_class == "진료":
                    month_j_colon += 1
                elif patient.exam_class == "건진+진료":
                    month_j_colon += 1

            if 'S' in patient.exam_type: month_sig += 1

    context['month_g_egd'] = month_g_egd
    context['month_j_egd'] = month_j_egd
    context['month_total_egd'] = month_g_egd + month_j_egd
    context['month_g_colon'] = month_g_colon
    context['month_j_colon'] = month_j_colon
    context['month_total_colon'] = month_g_colon + month_j_colon
    context['month_sig'] = month_sig
    context['first_colon'] = first_colon
    context['second_colon'] = second_colon
    if first_colon != 0:
        context['first_polyp_rate'] = int(float(first_polyp) / first_colon * 100)
        context['first_adenoma_rate'] = int(float(first_adenoma) / first_colon * 100)
    else:
        context['first_polyp_rate'], context['first_adenoma_rate'] = '0','0'
    if second_colon != 0:
        context['second_polyp_rate'] = int(float(second_polyp) / second_colon * 100)
        context['second_adenoma_rate'] = int(float(second_adenoma) / second_colon * 100)
    else:
        context['second_polyp_rate'],context['second_adenoma_rate'] = '0','0'

    if context['month_total_colon']!=0:
        context['total_polyp_rate']=int(float(first_polyp+second_polyp)/context['month_total_colon']*100)
        context['total_adenoma_rate']=int(float(first_adenoma+second_adenoma)/context['month_total_colon']*100)
    else :
        context['total_polyp_rate'], context['total_adenoma_rate']='0','0'

    return render(request, 'home.html', context)


#test



