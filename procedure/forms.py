from django import forms
from procedure.models import Exam

class ProcedureSearchForm(forms.Form):
    search_word=forms.CharField(label="이름 or 등록번호")
