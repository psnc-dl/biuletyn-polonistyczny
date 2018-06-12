# -*- coding: utf-8 -*-
from cities_light.models import City, Region
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.common.models import TargetGroup
from bportal.module.institution.models import Institution

from .fields import FieldScholarship, FieldScholarshipFilter
from .models import ScholarshipType, Scholarship


class ScholarshipFilterForm(forms.ModelForm):
    
    SCHOLARSHIP_STATUS_IN_PROGRESS = 'IN_PROGRESS'
    SCHOLARSHIP_STATUS_FINISHED = 'FINISHED'
    
    SCHOLARSHIP_STATUSES = (
        (SCHOLARSHIP_STATUS_IN_PROGRESS, 'Oferta otwarta'),
        (SCHOLARSHIP_STATUS_FINISHED, 'Oferta zakończona'),
    )
    scholarship_status = forms.MultipleChoiceField(label=FieldScholarshipFilter.STATUS, required=False,
                                                             choices=SCHOLARSHIP_STATUSES,
                                                             widget=autocomplete.Select2Multiple(attrs={'class': 'select2'}))
    scholarship_only_my = forms.BooleanField(label=FieldScholarshipFilter.ONLY_MY, required=False)        
    
    class Meta:
        model = Scholarship
        fields = ('scholarship_status', 'scholarship_only_my')


class ScholarshipFilter(django_filters.FilterSet):
    scholarship_founder = django_filters.ModelChoiceFilter(label=FieldScholarship.FOUNDER,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='institution-autocomplete'))
    scholarship_name_text = django_filters.CharFilter(label=FieldScholarship.NAME, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    scholarship_targets = django_filters.ModelMultipleChoiceFilter(label=FieldScholarship.TARGETS,
                                                             queryset=TargetGroup.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='targetgroup-autocomplete'))
    scholarship_type = django_filters.ModelMultipleChoiceFilter(label=FieldScholarship.TYPE,
                                                             queryset=ScholarshipType.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='scholarshiptype-autocomplete'))
    scholarship_city__region = django_filters.ModelChoiceFilter(label=FieldScholarship.REGION,
                                                             queryset=Region.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='region-autocomplete'))
    scholarship_city = django_filters.ModelChoiceFilter(label=FieldScholarship.CITY,
                                                             queryset=City.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='city-autocomplete'))
    scholarship_date_start = django_filters.DateFilter(label=FieldScholarship.DATE_START, lookup_expr='gte', widget=forms.DateInput(attrs={'class': 'datepicker list__form--input'}))
    scholarship_date_end = django_filters.DateFilter(label=FieldScholarship.DATE_END, lookup_expr='lte', widget=forms.DateInput(attrs={'class': 'datepicker list__form--input'}))
    scholarship_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldScholarship.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    scholarship_is_accepted = django_filters.BooleanFilter(label=FieldScholarship.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))
    
    o = django_filters.OrderingFilter(
        fields=(
            ('scholarship_is_promoted', 'scholarship_is_promoted'),
            ('scholarship_date_add', 'scholarship_date_add'),
            ('scholarship_name_text', 'scholarship_name_text'),
            ('scholarship_date_end', 'scholarship_date_end'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = Scholarship
        form = ScholarshipFilterForm
        fields = ['scholarship_founder', 'scholarship_name_text',
                  'scholarship_targets', 'scholarship_type',
                  'scholarship_city__region', 'scholarship_city',
                  'scholarship_date_start', 'scholarship_date_end',
                  'scholarship_keywords', 'scholarship_is_accepted']
