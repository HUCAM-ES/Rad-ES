from django.shortcuts import render
from django.views.generic import View, TemplateView, ListView, DetailView, FormView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.http import JsonResponse

from dose_app.forms import SearchForm, NameListForm
from dose_app.models import ModelPatient, ModelStudyXA, ModelDeletedUID
from dose_app.models import ModelRequestName, ModelRequestUIDs, ModelRequestDatePeriod, ModelRequestDateFixed
from dose_app.script import convert_date_dash, fix_name_string, sum_total, statistic_studies
from dose_app.script import create_models_by_name, create_models_by_date_fixed, database_update
from dose_app.script import create_models_by_date_period_fast, statistic_by_date, program_update
from dose_app.filters import XAListFilter, PatientListFilter

import json, datetime

#Logins
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
# Pagina inicial
class Index(TemplateView, FormMixin):
    form_class = SearchForm
    template_name = 'dose_app/index.html'
    success_url = reverse_lazy('dose_app:index')

    def post(self, *args, **kwargs):
        if 'btn_db_update' in list(self.request.POST.keys()):
            if self.request.POST['radioDataInput'] == '':
                db_updated = database_update(False)
                pass
            else:
                db_updated = database_update(True, self.request.POST['radioDataInput'])

        elif 'btn_prog_update' in list(self.request.POST.keys()):
            print("#----------------------------------------------------------------------#")
            prog_updated = program_update()
            print("#----------------------------------------------------------------------#")
            #for patient_model in ModelPatient.objects.all():
            #    patient_model.number_of_studies = 0
            #    patient_model.dose_PKA_complete = 0
            #    patient_model.dose_KAPR_complete = 0
            #    patient_model.save()
            #    for study in patient_model.xa_studies.all():
            #        patient_model.number_of_studies += 1
            #        patient_model.dose_PKA_complete += study.dose_PKA_total
            #        patient_model.dose_KAPR_complete += study.dose_KAPR_total
            #        patient_model.save()

        return super(Index, self).form_valid(self.get_form())


# Informacao estatistica da pagina
class StatisticInfoXA(ListView):
    model = ModelStudyXA
    template_name = 'dose_app/statistic_info_xa.html'
    context_object_name = 'patient_studies_all'

    # Definicao de contexto para inje�ao em html
    def get_context_data(self, **kwargs):

        if 'year' in list(self.request.GET.keys()):
            today_year=self.request.GET["year"]
            study_qs = self.model.objects.filter(study_date_parsed__year=today_year)
            est_PKA_total, est_KAPR_total, patient_month, study_month = statistic_studies(study_qs)
        else:
            today_year = datetime.date.today().year
            study_qs = self.model.objects.filter(study_date_parsed__year=today_year)
            est_PKA_total, est_KAPR_total, patient_month, study_month = statistic_studies(study_qs)

        qs = ModelPatient.objects.all()
        stats_bd = {}
        if 'date_before' in list(self.request.GET.keys()) and 'date_after' in list(self.request.GET.keys()):
            qs_studies = ModelStudyXA.objects.all()
            filtered_struct = XAListFilter({'date_before': self.request.GET['date_before'],
                                            'date_after': self.request.GET['date_after']},
                                           qs_studies, request=self.request)
            stats_bd = statistic_by_date(filtered_struct.qs)

        if 'dep_max' in list(self.request.GET.keys()):
            filtered_struct = PatientListFilter({'dose_KAPR_gte': str(self.request.GET["dep_max"])}, queryset=qs)
            if stats_bd == {}:
                stats_bd = statistic_by_date(self.model.objects.all())

        else:
            filtered_struct = PatientListFilter({'dose_KAPR_gte': '2000'}, queryset=qs)
            if stats_bd == {}:
                stats_bd = statistic_by_date(self.model.objects.all())

        data = {
            'est_PKA_total': est_PKA_total,
            'est_KAPR_total': est_KAPR_total,
            'patient_month': patient_month,
            'study_month': study_month,
            'filtered_data': filtered_struct.qs.order_by('dose_KAPR_complete'),
            'stats_by_date': stats_bd,
            'year': today_year,
        }

        return data

    # return super(XATotalDetailView, self).get_context_data(**context)

    # return super(XATotalDetailView, self).get_context_data(**context)

# Pagina de Teste de HTML (a ser deletado)
def test(request):
    return render(request, 'dose_app/test.html')


# Pagina Sobre o programa
def sobre(request):
    return render(request, 'dose_app/sobre.html')


# Pagina de Configuracoes do site (Nao implementado)
def config(request):
    return render(request, 'dose_app/configs.html')


# Pagina de Pesquisa de paciente
class SearchView(FormView):
    form_class = SearchForm
    template_name = 'dose_app/pesquisa.html'

    # Fun�ao chamada de Formulario for validado
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        self.form = form
        return super().form_valid(form)

    def get_success_url(self):

        if 'search_name' in list(self.request.POST.keys()):
            # Faz string maiuscula e retira acentos para pesquisa
            name_string = fix_name_string(self.form.cleaned_data['search_name'])
            create_models_by_name([name_string])
            # Adicona underline em nome para adi�ao em URL
            name_string = name_string.replace(' ', '_')
            return reverse_lazy('dose_app:lista', kwargs={'search_name': name_string})

        elif ('date_before' in list(self.request.POST.keys())) and ('date_after' in list(self.request.POST.keys())):
            create_models_by_date_period_fast(date_before=self.request.POST['date_before'],
                                              date_after=self.request.POST['date_after'])
            return reverse_lazy('dose_app:lista_data', kwargs={'date_before': self.request.POST['date_before'],
                                                               'date_after': self.request.POST['date_after']})

        else:
            return reverse_lazy('dose_app:pesquisa')


class StudyListView(ListView, FormMixin):
    model = ModelPatient
    form_class = NameListForm
    id_string = ''
    template_name = 'dose_app/lista_estudos.html'


    def post(self, request, *args, **kwargs):
        print(request.POST)
        if 'group_checkboxes' in list(request.POST.keys()) or 'delete_checkboxes' in list(request.POST.keys()):
            if 'group' in request.POST:
                patient_list_id = ModelPatient.objects.all().values('id').filter(id__in=request.POST.getlist('group_checkboxes'))
                self.id_string = ''.join((str(patient_list_id[i]['id'])+'e') if (i != len(patient_list_id)-1)
                                   else str(patient_list_id[i]['id']) for i in range(len(patient_list_id)))
                self.type = 'p'
            elif 'delete' in request.POST:
                patient_list = ModelPatient.objects.filter(id__in=request.POST.getlist('delete_checkboxes'))
                for patient in patient_list:
                    for study in patient.xa_studies.all():
                        ModelDeletedUID.objects.get_or_create(del_uid=study.uid)
                        study.delete()
                    patient.delete()


        elif 'group_checkboxes_study' in list(request.POST.keys()) or 'delete_checkboxes_study' in list(request.POST.keys()):
            if 'group' in request.POST:
                study_list_id = ModelStudyXA.objects.all().values('id').filter(id__in=request.POST.getlist('group_checkboxes_study'))
                self.id_string = ''.join((str(study_list_id[i]['id']) + 'e') if (i != len(study_list_id) - 1)
                                         else str(study_list_id[i]['id']) for i in range(len(study_list_id)))
                self.type = 's'
            elif 'delete' in request.POST:
                study_list = ModelStudyXA.objects.filter(id__in=request.POST.getlist('delete_checkboxes_study'))
                for study in study_list:
                    ModelDeletedUID.objects.get_or_create(del_uid=study.uid)
                    study.delete()

        return super(StudyListView, self).form_valid(self.get_form())

    def get_success_url(self, **kwargs):
        if 'group' in self.request.POST:
            return reverse_lazy('dose_app:grupo_detalhes_total', kwargs={'search_name': self.kwargs['search_name'],
                                                                         'id_group': self.id_string, 'type': self.type})
        else:
            return reverse_lazy('dose_app:lista', kwargs={'search_name': self.kwargs['search_name']})

    def get_context_data(self, **kwargs):

        model_list = ModelPatient.objects.filter(name__icontains=(self.kwargs['search_name']).replace('_', ' '))
        study_list = []
        for patient in model_list:
            for study in patient.xa_studies.all():
                study_list.append(study)
        context = {
            'patient_list': model_list,
            'study_list': study_list,
        }
        return super(StudyListView, self).get_context_data(**context)


class StudyListViewByDate(ListView, FormMixin):
    model = ModelPatient
    form_class = NameListForm
    context_object_name = 'patient_list'
    template_name = 'dose_app/lista_estudos_data.html'
    id_string = ''

    def get_queryset(self):
        qs_studies = ModelStudyXA.objects.all()
        filtered_struct = XAListFilter({'date_before': self.kwargs['date_before'],
                                        'date_after': self.kwargs['date_after']}, qs_studies, request=self.request)
        study_list = filtered_struct.qs.all()
        model_list = []
        for study in study_list:
            if study.patient not in model_list:
                model_list.append(study.patient)
        return model_list

    def post(self, request, *args, **kwargs):
        print(request.POST)
        if 'group_checkboxes' in list(request.POST.keys()) or 'delete_checkboxes' in list(request.POST.keys()):
            if 'group' in request.POST:
                patient_list_id = ModelPatient.objects.all().values('id').filter(
                    id__in=request.POST.getlist('group_checkboxes'))
                self.id_string = ''.join((str(patient_list_id[i]['id']) + 'e') if (i != len(patient_list_id) - 1)
                                         else str(patient_list_id[i]['id']) for i in range(len(patient_list_id)))
                self.type = 'p'
            elif 'delete' in request.POST:
                patient_list = ModelPatient.objects.filter(id__in=request.POST.getlist('delete_checkboxes'))
                for patient in patient_list:
                    for study in patient.xa_studies.all():
                        ModelDeletedUID.objects.get_or_create(del_uid=study.uid)
                        study.delete()
                    patient.delete()

        elif 'group_checkboxes_study' in list(request.POST.keys()) or 'delete_checkboxes_study' in list(
                request.POST.keys()):
            if 'group' in request.POST:
                study_list_id = ModelStudyXA.objects.all().values('id').filter(
                    id__in=request.POST.getlist('group_checkboxes_study'))
                self.id_string = ''.join((str(study_list_id[i]['id']) + 'e') if (i != len(study_list_id) - 1)
                                         else str(study_list_id[i]['id']) for i in range(len(study_list_id)))
                self.type = 's'
            elif 'delete' in request.POST:
                study_list = ModelStudyXA.objects.filter(id__in=request.POST.getlist('delete_checkboxes_study'))
                for study in study_list:
                    ModelDeletedUID.objects.get_or_create(del_uid=study.uid)
                    study.delete()

        return super(StudyListViewByDate, self).form_valid(self.get_form())

    def get_success_url(self, **kwargs):
        if 'group' in self.request.POST:
            return reverse_lazy('dose_app:grupo_detalhes_total_data', kwargs={'date_before': self.kwargs['date_before'],
                                                                              'date_after': self.kwargs['date_after'],
                                                                              'id_group': self.id_string, 'type': self.type})
        else:
            return reverse_lazy('dose_app:lista_data', kwargs={'date_before': self.kwargs['date_before'],
                                                               'date_after': self.kwargs['date_after']})

    def get_context_data(self, **kwargs):

        qs_studies = ModelStudyXA.objects.all()
        filtered_struct = XAListFilter({'date_before': self.kwargs['date_before'],
                                        'date_after': self.kwargs['date_after']}, qs_studies, request=self.request)
        study_list = filtered_struct.qs.all()
        model_list = []
        for study in study_list:
            if study.patient not in model_list:
                model_list.append(study.patient)

        context = {
            'patient_list': model_list,
            'study_list': study_list,
        }
        return super(StudyListViewByDate, self).get_context_data(**context)


class XADetailView(DetailView):
    model = ModelPatient
    template_name = 'dose_app/detalhe_estudo.html'
    context_object_name = 'xa_details'

    def get_object(self):
        model_patient = ModelPatient.objects.get(id=self.kwargs['pk'])
        model_study = model_patient.xa_studies.get(id=self.kwargs['ppk'])
        return model_study


class XATotalDetailView(ListView):
    model = ModelStudyXA
    template_name = 'dose_app/detalhe_estudo_total.html'

    def get_context_data(self, **kwargs):
        qs = ModelPatient.objects.get(id=self.kwargs['pk']).xa_studies.all()
        if len(self.request.GET) > 0:
            filtered_struct = XAListFilter({'date_after': self.request.GET['date_after'],
                                            'date_before': self.request.GET['date_before'],
                                            'PKA_tot_max': self.request.GET['PKA_tot_max'],
                                            'PKA_tot_min': self.request.GET['PKA_tot_min'],
                                            'KAPR_tot_max': self.request.GET['KAPR_tot_max'],
                                            'KAPR_tot_min': self.request.GET['KAPR_tot_min'],
                                            }, qs, request=self.request)
        else:
            filtered_struct = XAListFilter(self.request.GET, qs, request=self.request)
        sum_total_filtered = sum_total(filtered_struct.qs)
        stats_bd = {
            "fluoro_time_total": 0,
            "acq_time_total": 0,
            "fluoro_PKA_total": 0,
            "fluoro_KAPR_total": 0,
            "acq_PKA_total": 0,
            "acq_KAPR_total": 0,
            "dose_PKA_total": 0,
            "dose_KAPR_total": 0,
        }
        if len(filtered_struct.qs) > 0:
            stats_bd = statistic_by_date(filtered_struct.qs)

        context = {
            'filtered_data': filtered_struct.qs.order_by('study_date_parsed'),
            'sum_total_filtered': sum_total_filtered,
            'stats_by_date': stats_bd,
        }
        return super(XATotalDetailView, self).get_context_data(**context)


class XATotalDetailViewData(ListView):
    model = ModelStudyXA
    template_name = 'dose_app/detalhe_estudo_total_data.html'

    def get_context_data(self, **kwargs):
        qs = ModelPatient.objects.get(id=self.kwargs['pk']).xa_studies.all()
        if len(self.request.GET) > 0:
            filtered_struct = XAListFilter({'date_after': self.request.GET['date_after'],
                                            'date_before': self.request.GET['date_before'],
                                            'PKA_tot_max': self.request.GET['PKA_tot_max'],
                                            'PKA_tot_min': self.request.GET['PKA_tot_min'],
                                            'KAPR_tot_max': self.request.GET['KAPR_tot_max'],
                                            'KAPR_tot_min': self.request.GET['KAPR_tot_min'],
                                            }, qs, request=self.request)
        else:
            filtered_struct = XAListFilter(self.request.GET, qs, request=self.request)
        sum_total_filtered = sum_total(filtered_struct.qs)
        stats_bd = {
            "fluoro_time_total": 0,
            "acq_time_total": 0,
            "fluoro_PKA_total": 0,
            "fluoro_KAPR_total": 0,
            "acq_PKA_total": 0,
            "acq_KAPR_total": 0,
            "dose_PKA_total": 0,
            "dose_KAPR_total": 0,
        }
        if len(filtered_struct.qs) > 0:
            stats_bd = statistic_by_date(filtered_struct.qs)

        context = {
            'filtered_data': filtered_struct.qs.order_by('study_date_parsed'),
            'sum_total_filtered': sum_total_filtered,
            'stats_by_date': stats_bd,
        }
        return super(XATotalDetailViewData, self).get_context_data(**context)


class XATotalDetailViewGroup(ListView):
    model = ModelStudyXA
    template_name = 'dose_app/detalhe_estudo_total.html'

    def get_context_data(self, **kwargs):
        id_list = self.kwargs['id_group'].split('e')
        study_list = [i['xa_studies'] for i in ModelPatient.objects.values('xa_studies').filter(id__in=id_list)]
        qs = ModelStudyXA.objects.filter(id__in=study_list)
        if len(self.request.GET) > 0:
            filtered_struct = XAListFilter({'date_after': self.request.GET['date_after'],
                                            'date_before': self.request.GET['date_before'],
                                            'PKA_tot_max': self.request.GET['PKA_tot_max'],
                                            'PKA_tot_min': self.request.GET['PKA_tot_min'],
                                            'KAPR_tot_max': self.request.GET['KAPR_tot_max'],
                                            'KAPR_tot_min': self.request.GET['KAPR_tot_min'],
                                            }, qs, request=self.request)
        else:
            filtered_struct = XAListFilter(self.request.GET, qs, request=self.request)
        sum_total_filtered = sum_total(filtered_struct.qs)

        stats_bd = {
            "fluoro_time_total": 0,
            "acq_time_total": 0,
            "fluoro_PKA_total": 0,
            "fluoro_KAPR_total": 0,
            "acq_PKA_total": 0,
            "acq_KAPR_total": 0,
            "dose_PKA_total": 0,
            "dose_KAPR_total": 0,
        }
        if len(filtered_struct.qs) > 0:
            stats_bd = statistic_by_date(filtered_struct.qs)

        context = {
            'filtered_data': filtered_struct.qs.order_by('study_date_parsed'),
            'sum_total_filtered': sum_total_filtered,
            'stats_by_date': stats_bd,
        }
        return super(XATotalDetailViewGroup, self).get_context_data(**context)


class XATotalDetailViewGroupData(ListView):
    model = ModelStudyXA
    template_name = 'dose_app/detalhe_estudo_total_data.html'

    def get_context_data(self, **kwargs):
        id_list = self.kwargs['id_group'].split('e')
        study_list = [i['xa_studies'] for i in ModelPatient.objects.values('xa_studies').filter(id__in=id_list)]
        qs = ModelStudyXA.objects.filter(id__in=study_list)
        if len(self.request.GET) > 0:
            filtered_struct = XAListFilter({'date_after': self.request.GET['date_after'],
                                            'date_before': self.request.GET['date_before'],
                                            'PKA_tot_max': self.request.GET['PKA_tot_max'],
                                            'PKA_tot_min': self.request.GET['PKA_tot_min'],
                                            'KAPR_tot_max': self.request.GET['KAPR_tot_max'],
                                            'KAPR_tot_min': self.request.GET['KAPR_tot_min'],
                                            }, qs, request=self.request)
        else:
            filtered_struct = XAListFilter(self.request.GET, qs, request=self.request)
        sum_total_filtered = sum_total(filtered_struct.qs)

        stats_bd = {
            "fluoro_time_total": 0,
            "acq_time_total": 0,
            "fluoro_PKA_total": 0,
            "fluoro_KAPR_total": 0,
            "acq_PKA_total": 0,
            "acq_KAPR_total": 0,
            "dose_PKA_total": 0,
            "dose_KAPR_total": 0,
        }
        if len(filtered_struct.qs) > 0:
            stats_bd = statistic_by_date(filtered_struct.qs)

        context = {
            'filtered_data': filtered_struct.qs.order_by('study_date_parsed'),
            'sum_total_filtered': sum_total_filtered,
            'stats_by_date': stats_bd,
        }
        return super(XATotalDetailViewGroupData, self).get_context_data(**context)


# ####################################### LOGIN REQUIRED SECTION ######################################################

@login_required
def hucam_server_comm_in(request):
    if request.method == "POST":
        received_json_data = json.loads(request.body.decode("utf-8").split('&')[0].split('=')[1])
        if received_json_data['type'] == 'date_fixed':
            req = ModelRequestDateFixed.objects.get(id=received_json_data['id'])
        elif received_json_data['type'] == 'date_period':
            req = ModelRequestDatePeriod.objects.get(id=received_json_data['id'])
        elif received_json_data['type'] == 'uid':
            req = ModelRequestUIDs.objects.get(id=received_json_data['id'])
        else:
            req = ModelRequestName.objects.get(id=received_json_data['id'])
        req.ready = True
        req.full_info = json.dumps(received_json_data['full_info'])
        req.save()

    return render(request, 'dose_app/comm_in.html')


@login_required
def hucam_server_comm_out(request):
    requests = {
        'tasks_name': [],
        'tasks_uid': [],
        'tasks_date_fixed': [],
        'tasks_date_period': [],
    }
    for req in ModelRequestName.objects.filter(ready=False):
        requests['tasks_name'].append([req.name, req.id, req.priority, 'name', req.ready])

    for req in ModelRequestUIDs.objects.filter(ready=False):
        requests['tasks_uid'].append([req.uids, req.id, req.priority, 'uid',  req.ready])

    for req in ModelRequestDateFixed.objects.filter(ready=False):
        requests['tasks_date_fixed'].append([[req.days_back, req.months_back], req.id, req.priority, 'date_fixed', req.ready])

    for req in ModelRequestDatePeriod.objects.filter(ready=False):
        requests['tasks_date_period'].append([[req.date_before, req.date_after], req.id, req.priority, 'date_period', req.ready])

    return JsonResponse(requests)


@login_required
def hucam_server_comm_update(request):
    requests = {
        'done': False,
    }
    name_string = list(ModelPatient.objects.all().values_list('name', flat=True))
    created = create_models_by_name(name_string)
    if created:
        print('All models created successfully')
    elif created == False:
        print('No studies received from patient data')
    else:
        print('Query passed')

    created = create_models_by_date_fixed(number_of_days=1, number_of_months=0)
    if created:
        print('All models created successfully')
    elif created == False:
        print('No studies received from patient data')
    else:
        print('Query passed')
    requests['done'] = True

    return JsonResponse(requests)