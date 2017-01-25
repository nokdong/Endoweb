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
from procedure.forms import ProcedureSearchForm, DurationStaticForm
from procedure.models import Exam
from bokeh.plotting import figure, show, save, output_file
from bokeh.layouts import column
from bokeh.models.widgets import Panel, Tabs


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

        return render(self.request, self.template_name, context)

class DurationStatic(LoginRequiredMixin, FormView):
    form_class = DurationStaticForm
    template_name = 'procedure/duration_static.html'

    def form_valid(self, form):
        first_date=self.request.POST['first_date']
        last_date=self.request.POST['last_date']

        context={}
        object_list=Exam.objects.filter(Q(exam_date__gte=first_date) & Q(exam_date__lte=last_date))
        object_list.order_by('exam_date')
        print (object_list)
        context['form'] = form
        context['object_list']=object_list


        return render(self.request, self.template_name, context)




class BxUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','follow_up']
    success_url = reverse_lazy('procedure:biopsy')

class SearchUpdateview(LoginRequiredMixin, UpdateView):
    model=Exam
    fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
              'patient_sex', 'patient_birth','patient_phone','exam_Dx', 'exam_procedure','Bx_result','follow_up',
              'phone_check','re_visit']
    template_name = 'procedure/post_search_update.html'
    success_url = reverse_lazy('procedure:search')

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
    all_patients=Exam.objects.all()
    context={'object_list':[],'g_egd':0, 'j_egd':0, 'total_egd':0, 'g_colon':0, 'j_colon':0, 'total_colon':0, 'sig':0, 'first_colon':0,
             'first_polyp_rate':0, 'first_adr':0, 'second_colon':0, 'second_polyp_rate':0, 'second_adr':0,
             'total_polyp_rate':0, 'total_adenoma_rate':0}
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
                    if 'adenoma' in patient.Bx_result:
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

    return (monthly_egd, monthly_colon)

@login_required
def graph(request):
    data=year_data()
    data_source = SimpleDataSource(data=data)
    chart = ColumnChart(data_source, options={'title': "올해 내시경 추이"})
    context = {'chart': chart}
    return render(request, 'procedure/year_graph.html', context)

def homegraph(request):
    egd_2015 = {1:436, 2:298, 3:155, 4:110, 5:54, 6:65, 7:67, 8:51, 9:61, 10:85, 11:114, 12:185}
    colon_2015 ={1:19, 2:12, 3:29, 4:27, 5:11, 6:4, 7:19, 8:8, 9:10, 10:15, 11:19, 12:38}
    egd_2016 = {1:291, 2:219, 3:102, 4:84, 5:65, 6:92, 7:73, 8:79, 9:70, 10:84, 11:123, 12:163}
    colon_2016 = {1:20, 2:23, 3:40, 4:43, 5:30, 6:35, 7:28, 8:29, 9:17, 10:21, 11:29, 12:50}

    today = date.today()
    monthly_egd, monthly_colon = year_data(today.year)

    egd = figure(x_axis_type ='datetime', x_axis_label ='월', y_axis_label = '개수', width=1000, height=350)
    egd.vbar(x=[1,2,3,4,5,6,7,8,9,10,11,12], width=0.5, bottom=0,
           top=list(monthly_egd.values()), color='firebrick', alpha = 0.5, legend = '2017')
    egd.circle([1,2,3,4,5,6,7,8,9,10,11,12],list(egd_2016.values()), size = 10,  color='navy', legend = '2016')
    egd.circle([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], list(egd_2015.values()), size=10, color='DarkCyan', legend = '2015')
    egd_tab = Panel(child = egd, title = "위내시경 추이")

    colon = figure(x_axis_type ='datetime', x_axis_label ='월', y_axis_label = '개수',width = 1000, height=350)
    colon.vbar(x=[1,2,3,4,5,6,7,8,9,10,11,12], width=0.5, bottom=0,
           top=list(monthly_colon.values()), color='blue', alpha = 0.5, legend = "2017")
    colon.circle([1,2,3,4,5,6,7,8,9,10,11,12],list(colon_2016.values()), size = 10,  color='Red', legend = '2016')
    colon.circle([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], list(colon_2015.values()), size=10,  color='HotPink',
                 legend='2015')
    colon_tab = Panel(child=colon, title = "대장내시경 추이")
    colon.legend.location = 'top_center'

    layout = Tabs(tabs = [egd_tab, colon_tab])

    output_file('procedure/vbar.html')
    save(layout)
    return render(request, 'procedure/vbar.html')
    '''
    data=year_data()
    data_source = SimpleDataSource(data=data)
    chart = ColumnChart(data_source, options={'title': "올해 내시경 추이"})
    context = {'chart': chart}
    return render(request, 'procedure/home_year_graph.html', context) '''

def home(request):
    none_Bx = 0  # Bx 결과 안들어 간 사람
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

    all_patients = Exam.objects.all()
    context = {'none_Bx': 0, 'none_reading': 0, 'will_phone': 0,
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
        if patient.exam_procedure in [['EMR'],['Polypectomy'], ['Bx']] and patient.Bx_result=='.':
            none_Bx+=1
    context['none_Bx']=none_Bx

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

''' testing'''





