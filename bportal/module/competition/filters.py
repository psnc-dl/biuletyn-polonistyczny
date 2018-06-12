# -*- coding: utf-8 -*-
from cities_light.models import City, Region
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.common.models import TargetGroup
from bportal.module.institution.models import Institution

from .fields import FieldCompetition, FieldCompetitionFilter
from .models import Competition


class CompetitionFilterForm(forms.ModelForm):
    
    COMPETITION_STATUS_IN_PROGRESS = 'IN_PROGRESS'
    COMPETITION_STATUS_FINISHED = 'FINISHED'
    
    COMPETITION_STATUSES = (
        (COMPETITION_STATUS_IN_PROGRESS, 'Konkurs otwarty'),
        (COMPETITION_STATUS_FINISHED, 'Konkurs zakończony'),
    )
    competition_status = forms.MultipleChoiceField(label=FieldCompetitionFilter.STATUS, required=False,
                                                             choices=COMPETITION_STATUSES,
                                                             widget=autocomplete.Select2Multiple(attrs={'class': 'select2'}))
    competition_only_my = forms.BooleanField(label=FieldCompetitionFilter.ONLY_MY, required=False) 
        
    class Meta:
        model = Competition
        fields = ('competition_status', 'competition_only_my')


class CompetitionFilter(django_filters.FilterSet):
    competition_institutions = django_filters.ModelChoiceFilter(label=FieldCompetition.INSTITUTION,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='institution-autocomplete'))
    competition_title_text = django_filters.CharFilter(label=FieldCompetition.TITLE, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    competition_targets = django_filters.ModelMultipleChoiceFilter(label=FieldCompetition.TARGETS,
                                                             queryset=TargetGroup.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='targetgroup-autocomplete'))
    competition_city__region = django_filters.ModelChoiceFilter(label=FieldCompetition.REGION,
                                                             queryset=Region.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='region-autocomplete'))
    competition_city = django_filters.ModelChoiceFilter(label=FieldCompetition.CITY,
                                                             queryset=City.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='city-autocomplete'))
    competition_deadline_date = django_filters.DateFilter(label=FieldCompetition.DEADLINE_DATE, lookup_expr='lte', widget=forms.DateInput(attrs={'class': 'datepicker list__form--input'}))
    competition_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldCompetition.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    competition_is_accepted = django_filters.BooleanFilter(label=FieldCompetition.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'})) 

    o = django_filters.OrderingFilter(
        fields=(
            ('competition_is_promoted', 'competition_is_promoted'),
            ('competition_date_add', 'competition_date_add'),
            ('competition_title_text', 'competition_title_text'),
            ('competition_deadline_date', 'competition_deadline_date'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = Competition
        form = CompetitionFilterForm
        fields = ['competition_institutions', 'competition_title_text',
                  'competition_targets', 'competition_city__region',
                  'competition_city', 'competition_deadline_date',
                  'competition_keywords', 'competition_is_accepted']
