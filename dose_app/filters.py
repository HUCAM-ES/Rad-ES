from django import forms

import django_filters
from dose_app import models
import datetime


# Filtra por estudos utilizando parametros apresentados em Form na lateral da pagina
class XAListFilter(django_filters.FilterSet):

    date_after = django_filters.DateFilter(lookup_expr='lte', field_name='study_date_parsed')
    date_before = django_filters.DateFilter(lookup_expr='gte', field_name='study_date_parsed')

    PKA_tot_max = django_filters.NumberFilter(lookup_expr='lte', field_name='dose_PKA_total')
    PKA_tot_min = django_filters.NumberFilter(lookup_expr='gte', field_name='dose_PKA_total')

    KAPR_tot_max = django_filters.NumberFilter(lookup_expr='lte', field_name='dose_KAPR_total')
    KAPR_tot_min = django_filters.NumberFilter(lookup_expr='gte', field_name='dose_KAPR_total')

    def filter_queryset(self, queryset):

        for name, value in self.data.items():
            if name == 'date_before' or name == 'date_after':
                if value is not '':
                    queryset = self.filters[name].filter(queryset, datetime.datetime.strptime(value,'%Y-%m-%d'))
            else:
                if value is not '':
                    queryset = self.filters[name].filter(queryset, value)

        return queryset


    class Meta:
        model = models.ModelStudyXA
        fields = ['date_after', 'date_before', 'PKA_tot_max', 'PKA_tot_min',  'KAPR_tot_max',  'KAPR_tot_min']
        #fields = []


# Filtra por paciente com Dose de entrada na pele acima de 2000 ou valor inserido por usuario
class PatientListFilter(django_filters.FilterSet):


    dose_KAPR_gte = django_filters.NumberFilter(lookup_expr='gte', field_name='dose_KAPR_complete')

    class Meta:
        model = models.ModelPatient
        fields = {'dose_KAPR_gte'}
