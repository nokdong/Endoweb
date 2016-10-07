import time
from datetime import date

from procedure.models import Exam
from django import forms

from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from django.views.generic.edit import FormView
from procedure.forms import ProcedureSearchForm
from django.db.models import Q
from django.shortcuts import render

from django.core.urlresolvers import reverse_lazy

from django.views.generic.base import TemplateView

class HomeView(TemplateView):
    template_name="home.html"

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


