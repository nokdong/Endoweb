from django.contrib import admin
from procedure.models import Exam


class ExamAdmin(admin.ModelAdmin):
    list_display=('exam_date','patient_name', 'hospital_no')
    list_filter=['exam_date']
    search_fields=('patient_name','hospital_no')

admin.site.register(Exam, ExamAdmin)