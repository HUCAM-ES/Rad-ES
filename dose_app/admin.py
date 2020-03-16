from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.template.loader import render_to_string

from dose_app.models import ModelStudyXA, ModelPatient, ModelDeletedUID
from dose_app.models import ModelRequestName, ModelRequestUIDs, ModelRequestDatePeriod, ModelRequestDateFixed


def set_unready(modeladmin, request, queryset):
    queryset.update(ready=False)


def set_undeleted(modeladmin, request, queryset):
    queryset.update(deleted=False)
set_undeleted.short_description = "Definir paciente como Não Deletados"


class patientAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'dob_parsed', 'dose_KAPR_complete', 'deleted')
    ordering = ['name']
    actions = [set_undeleted]
    change_list_template = "dose_app/patient_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('sendEmail/', self.send_email),
        ]
        return my_urls + urls

    def send_email(self, request):
        patient_qs = self.model.objects.all().filter(dose_KAPR_complete__gte=2000).order_by('dose_KAPR_complete')
        #message_alert_patients = ''.join((patient.name + ', '
        #                                  + str(patient.dob_parsed) + ', '
        #                                  + str(patient.dose_rp_complete) + ', '
        #                                  + str(patient.dose_area_complete) + ', '
        #                                  + str(patient.number_of_studies)+ ' .\n') for patient in patient_qs )
        #self.message_user(request, "Got all patients")
        #print(message_alert_patients)
        msg_html = render_to_string('dose_app/email_patient_alert.html', {'qs': patient_qs})
        send_mail(
            'HUCAM Dose - Lista de Pacientes em estado Critico',
            'teste hmtl', #message_alert_patients,
            'doses.hucam@gmail.com',
            ['vervoltz@gmail.com'],
            html_message=msg_html,
            fail_silently=False,
        )
        return HttpResponseRedirect("../")


class studyAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_name', 'study_date_parsed', 'study_time_parsed', 'dose_KAPR_total', 'dose_PKA_total', 'acq_time_total', 'fluoro_time_total', 'deleted')
    ordering = ['id']

    def get_name(self, obj):
        return obj.patient.name

    get_name.admin_order_field = 'patient__name'  # Allows column order sorting
    get_name.short_description = 'Patient Name'  # Renames column head


class requestAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'dob_parsed', 'dose_KAPR_complete', 'deleted')
    actions = [set_unready]


# Register your models here.
admin.site.register(ModelPatient, patientAdmin)
admin.site.register(ModelStudyXA, studyAdmin)
admin.site.register(ModelDeletedUID)

