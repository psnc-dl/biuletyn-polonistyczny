# -*- coding: utf-8 -*-
from cities_light.models import City, Region
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.common.models import TargetGroup
from bportal.module.institution.models import Institution

from .fields import FieldEvent, FieldEventFilter
from .models import EventCategory, Event


class EventFilterForm(forms.ModelForm):
    
    EVENT_STATUS_FURTHCOMING = 'FURTHCOMING'
    EVENT_STATUS_IN_PROGRESS = 'IN_PROGRESS'
    EVENT_STATUS_PAST = 'PAST'
    
    EVENT_STATUSES = (
        (EVENT_STATUS_FURTHCOMING, 'Nadchodzące'),
        (EVENT_STATUS_IN_PROGRESS, 'Bieżące'),
        (EVENT_STATUS_PAST, 'Minione'),
    )
    event_status = forms.MultipleChoiceField(label=FieldEventFilter.STATUS, required=False,
                                                             choices=EVENT_STATUSES,
                                                             widget=autocomplete.Select2Multiple(attrs={'class': 'select2'}))
    event_only_my = forms.BooleanField(label=FieldEventFilter.ONLY_MY, required=False) 
        
    class Meta:
        model = Event
        fields = ('event_status', 'event_only_my')
       

class EventFilter(django_filters.FilterSet):
    event_institutions = django_filters.ModelChoiceFilter(label=FieldEvent.INSTITUTIONS,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2('institution-autocomplete'))
    event_name_text = django_filters.CharFilter(label=FieldEvent.NAME, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    event_targets = django_filters.ModelMultipleChoiceFilter(label=FieldEvent.TARGETS,
                                                             queryset=TargetGroup.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='targetgroup-autocomplete'))
    event_category = django_filters.ModelMultipleChoiceFilter(label=FieldEvent.CATEGORIES,
                                                             queryset=EventCategory.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='eventcategory-autocomplete'))
    event_city__region = django_filters.ModelChoiceFilter(label=FieldEvent.REGION,
                                                             queryset=Region.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='region-autocomplete'))
    event_city = django_filters.ModelChoiceFilter(label=FieldEvent.CITY,
                                                             queryset=City.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='city-autocomplete'))
    event_date_from = django_filters.DateFilter(label=FieldEvent.DATE_FROM, lookup_expr='gte', widget=forms.DateTimeInput(attrs={'class': 'datepicker list__form--input'}))
    event_date_to = django_filters.DateFilter(label=FieldEvent.DATE_TO, lookup_expr='lte', widget=forms.DateTimeInput(attrs={'class': 'datepicker list__form--input'}))
    event_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldEvent.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    event_is_accepted = django_filters.BooleanFilter(label=FieldEvent.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))  
    
    o = django_filters.OrderingFilter(
        fields=(
            ('event_date_from', 'event_date_from'),
            ('event_time_from', 'event_time_from'),
        ),
    )    
        
    strict = True
    
    class Meta:
        model = Event
        form = EventFilterForm
        fields = ['event_institutions', 'event_name_text',
                  'event_targets', 'event_category',
                  'event_city__region', 'event_city',
                  'event_date_from', 'event_date_to',
                  'event_keywords', 'event_is_accepted']
