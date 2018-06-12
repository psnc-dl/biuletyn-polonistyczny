# -*- coding: utf-8 -*-
from cities_light.models import City, Region
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.common.models import ResearchDiscipline
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person

from .fields import FieldDissertation, FieldDissertationFilter
from .models import Dissertation


class DissertationFilterForm(forms.ModelForm):
    
    DISSERTATION_STATUS_IN_PROGRESS = 'IN_PROGRESS'
    DISSERTATION_STATUS_FINISHED = 'FINISHED'
    
    DISSERTATION_STATUSES = (
        (DISSERTATION_STATUS_IN_PROGRESS, 'Praca w toku'),
        (DISSERTATION_STATUS_FINISHED, 'Praca zakończona'),
    )
    dissertation_status = forms.MultipleChoiceField(label=FieldDissertationFilter.STATUS, required=False,
                                                             choices=DISSERTATION_STATUSES,
                                                             widget=autocomplete.Select2Multiple(attrs={'class': 'select2'}))
    dissertation_only_my = forms.BooleanField(label=FieldDissertationFilter.ONLY_MY, required=False)     
    
    class Meta:
        model = Dissertation
        fields = ('dissertation_status', 'dissertation_only_my')


class DissertationFilter(django_filters.FilterSet):
    dissertation_institution = django_filters.ModelChoiceFilter(label=FieldDissertation.INSTITUTION,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='institution-autocomplete'))
    dissertation_title_text = django_filters.CharFilter(label=FieldDissertation.TITLE, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    dissertation_author = django_filters.ModelChoiceFilter(label=FieldDissertation.AUTHOR,
                                                             queryset=Person.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='person-autocomplete'))
    dissertation_supervisors = django_filters.ModelChoiceFilter(label=FieldDissertation.SUPERVISORS,
                                                             queryset=Person.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='person-autocomplete'))
    dissertation_reviewers = django_filters.ModelChoiceFilter(label=FieldDissertation.REVIEWERS,
                                                             queryset=Person.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='person-autocomplete'))
    dissertation_disciplines = django_filters.ModelChoiceFilter(label=FieldDissertation.DISCIPLINES,
                                                             queryset=ResearchDiscipline.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='researchdiscipline-autocomplete'))
    dissertation_city__region = django_filters.ModelChoiceFilter(label=FieldDissertation.REGION,
                                                             queryset=Region.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='region-autocomplete'))
    dissertation_city = django_filters.ModelChoiceFilter(label=FieldDissertation.CITY,
                                                             queryset=City.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='city-autocomplete'))
    dissertation_date_start = django_filters.DateFilter(label=FieldDissertation.DATE_START, lookup_expr='gte', widget=forms.DateTimeInput(attrs={'class': 'datepicker list__form--input'}))
    dissertation_date_end = django_filters.DateFilter(label=FieldDissertation.DATE_END, lookup_expr='lte', widget=forms.DateTimeInput(attrs={'class': 'datepicker list__form--input'}))
    dissertation_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldDissertation.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    dissertation_is_accepted = django_filters.BooleanFilter(label=FieldDissertation.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))     

    o = django_filters.OrderingFilter(
        fields=(
            ('dissertation_is_promoted', 'dissertation_is_promoted'),
            ('dissertation_date_add', 'dissertation_date_add'),
            ('dissertation_title_text', 'dissertation_title_text'),
            ('dissertation_date_end', 'dissertation_date_end'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = Dissertation
        form = DissertationFilterForm
        fields = ['dissertation_institution', 'dissertation_title_text', 
                  'dissertation_author', 'dissertation_supervisors',
                  'dissertation_reviewers', 'dissertation_disciplines',
                  'dissertation_city__region', 'dissertation_city',
                  'dissertation_date_start', 'dissertation_date_end',
                  'dissertation_keywords', 'dissertation_is_accepted']
