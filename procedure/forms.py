from django import forms
from django.forms import widgets
from procedure.models import Exam

class ProcedureSearchForm(forms.Form):
    search_word=forms.CharField(label="이름 or 등록번호")

class DurationStaticForm(forms.Form):
    first_date=forms.DateField(label="처음 날짜")
    last_date=forms.DateField(label="마지막 날짜")
