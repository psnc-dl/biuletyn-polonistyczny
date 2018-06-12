# -*- coding: utf-8 -*-
from cities_light.models import City, Region
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.common.models import TargetGroup, ResearchDiscipline
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person

from .fields import FieldProject, FieldProjectFilter
from .models import Project


class ProjectFilterForm(forms.ModelForm):
    
    PROJECT_STATUS_IN_PROGRESS = 'IN_PROGRESS'
    PROJECT_STATUS_FINISHED = 'FINISHED'
    
    PROJECT_STATUSES = (
        (PROJECT_STATUS_IN_PROGRESS, 'W toku'),
        (PROJECT_STATUS_FINISHED, 'Zakończony'),
    )
    project_status = forms.MultipleChoiceField(label=FieldProjectFilter.STATUS, required=False,
                                                             choices=PROJECT_STATUSES,
                                                             widget=autocomplete.Select2Multiple(attrs={'class': 'select2'}))    
    project_only_my = forms.BooleanField(label=FieldProjectFilter.ONLY_MY, required=False)    
    
    
    class Meta:
        model = Project
        fields = ('project_status', 'project_only_my')



class ProjectFilter(django_filters.FilterSet):
    project_institutions = django_filters.ModelChoiceFilter(label=FieldProject.INSTITUTION,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='institution-autocomplete'))
    project_participants = django_filters.ModelChoiceFilter(label=FieldProject.PARTICIPANTS,
                                                             queryset=Person.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='person-autocomplete'))    
    project_title_text = django_filters.CharFilter(label=FieldProject.TITLE, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    project_targets = django_filters.ModelMultipleChoiceFilter(label=FieldProject.TARGETS,
                                                             queryset=TargetGroup.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='targetgroup-autocomplete'))
    project_disciplines = django_filters.ModelChoiceFilter(label=FieldProject.DISCIPLINES,
                                                             queryset=ResearchDiscipline.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='researchdiscipline-autocomplete'))
    project_cities__region = django_filters.ModelChoiceFilter(label=FieldProject.REGIONS,
                                                             queryset=Region.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='region-autocomplete'))
    project_cities = django_filters.ModelChoiceFilter(label=FieldProject.CITIES,
                                                             queryset=City.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='city-autocomplete'))
    project_date_start = django_filters.DateFilter(label=FieldProject.DATE_START, lookup_expr='gte', widget=forms.DateTimeInput(attrs={'class': 'datepicker list__form--input'}))
    project_date_end = django_filters.DateFilter(label=FieldProject.DATE_END, lookup_expr='lte', widget=forms.DateTimeInput(attrs={'class': 'datepicker list__form--input'}))
    project_financing = django_filters.CharFilter(label=FieldProject.FINANCING, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    project_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldProject.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))          
    project_is_accepted = django_filters.BooleanFilter(label=FieldProject.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))
    
    o = django_filters.OrderingFilter(
        fields=(
            ('project_is_promoted', 'project_is_promoted'),
            ('project_date_add', 'project_date_add'),
            ('project_title_text', 'project_title_text'),
            ('project_date_end', 'project_date_end'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = Project
        form = ProjectFilterForm
        fields = ['project_institutions', 'project_participants',
                  'project_title_text', 'project_targets',
                  'project_disciplines', 'project_cities__region',
                  'project_cities', 'project_date_start',
                  'project_date_end', 'project_financing', 
                  'project_keywords', 'project_is_accepted']
