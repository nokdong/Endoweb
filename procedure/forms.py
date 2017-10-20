from django import forms
from django.forms import widgets
from procedure.models import Exam
#from datetimewidget import widgets
    #.widgets import DateTimeWidget, DateWidget, TimeWidget
#from datetimewidget.widgets import DateWidget
#from bootstrap_datepicker.widgets import DatePicker
#from datetime import date

from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})

MONTHS = {
    1:'1', 2:'2', 3:'3', 4:'4',
    5:'5', 6:'6', 7:'7', 8:'8',
    9:'9', 10:'10', 11:'11', 12:'12'
}

class ProcedureSearchForm(forms.Form):
    search_word=forms.CharField(label="이름 or 등록번호 or 조직검사 결과 or 내시경 진단명", required=False)
    first_date = forms.DateField(label="처음 날짜",  required=False, widget=DateInput())
    last_date = forms.DateField(label="마지막 날짜", required=False, widget=DateInput())

class DurationStaticForm(forms.Form):
    first_date=forms.DateField(label="처음 날짜")
    last_date=forms.DateField(label="마지막 날짜")
