# -*- coding: utf-8 -*-
from cities_light.models import City, Region
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.institution.models import Institution

from .fields import FieldJobOffer, FieldJobOfferFilter
from .models import JobOfferDiscipline, JobOfferType, JobOffer


class JobOfferFilterForm(forms.ModelForm):
    
    JOBOFFER_STATUS_IN_PROGRESS = 'IN_PROGRESS'
    JOBOFFER_STATUS_FINISHED = 'FINISHED'
    
    JOBOFFER_STATUSES = (
        (JOBOFFER_STATUS_IN_PROGRESS, 'Rekrutacja w toku'),
        (JOBOFFER_STATUS_FINISHED, 'Rekrutacja zakończona'),
    )
    joboffer_status = forms.MultipleChoiceField(label=FieldJobOfferFilter.STATUS, required=False,
                                                             choices=JOBOFFER_STATUSES,
                                                             widget=autocomplete.Select2Multiple(attrs={'class': 'select2'}))
    joboffer_only_my = forms.BooleanField(label=FieldJobOfferFilter.ONLY_MY, required=False)     
    
    class Meta:
        model = JobOffer
        fields = ('joboffer_status', 'joboffer_only_my')


class JobOfferFilter(django_filters.FilterSet):
    joboffer_institution = django_filters.ModelChoiceFilter(label=FieldJobOffer.INSTITUTION,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='institution-autocomplete'))
    joboffer_position_text = django_filters.CharFilter(label=FieldJobOffer.POSITION, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    joboffer_type = django_filters.ModelMultipleChoiceFilter(label=FieldJobOffer.TYPE,
                                                             queryset=JobOfferType.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='joboffertype-autocomplete'))
    joboffer_disciplines = django_filters.ModelChoiceFilter(label=FieldJobOffer.DISCIPLINES,
                                                             queryset=JobOfferDiscipline.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='jobofferdiscipline-autocomplete'))    
    joboffer_cities__region = django_filters.ModelChoiceFilter(label=FieldJobOffer.REGIONS,
                                                             queryset=Region.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='region-autocomplete'))
    joboffer_cities = django_filters.ModelChoiceFilter(label=FieldJobOffer.CITIES,
                                                             queryset=City.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='city-autocomplete'))
    joboffer_date_start  = django_filters.DateFilter(label=FieldJobOffer.DATE_START, lookup_expr='gte', widget=forms.DateInput(attrs={'class': 'datepicker list__form--input'}))
    joboffer_date_end  = django_filters.DateFilter(label=FieldJobOffer.DATE_END, lookup_expr='lte', widget=forms.DateInput(attrs={'class': 'datepicker list__form--input'}))
    joboffer_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldJobOffer.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    joboffer_is_accepted = django_filters.BooleanFilter(label=FieldJobOffer.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))

    o = django_filters.OrderingFilter(
        fields=(
            ('joboffer_is_promoted', 'joboffer_is_promoted'),
            ('joboffer_date_add', 'joboffer_date_add'),
            ('joboffer_position_text', 'joboffer_position_text'),
            ('joboffer_date_end', 'joboffer_date_end'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = JobOffer
        form = JobOfferFilterForm
        fields = ['joboffer_institution', 'joboffer_position_text',
                  'joboffer_type', 'joboffer_disciplines',
                  'joboffer_cities__region', 'joboffer_cities',
                  'joboffer_date_start', 'joboffer_date_end',
                  'joboffer_keywords', 'joboffer_is_accepted']
