# -*- coding: utf-8 -*-
from cities_light.models import City, Region
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.institution.models import Institution

from .fields import FieldEducationalOffer, FieldEducationalOfferFilter
from .models import EducationalOfferMode, EducationalOfferType, EducationalOffer


class EducationalOfferFilterForm(forms.ModelForm):
    
    EDUOFFER_STATUS_IN_PROGRESS = 'IN_PROGRESS'
    EDUOFFER_STATUS_FINISHED = 'FINISHED'
    
    EDUOFFER_STATUSES = (
        (EDUOFFER_STATUS_IN_PROGRESS, 'Oferta otwarta'),
        (EDUOFFER_STATUS_FINISHED, 'Oferta zakończona'),
    )
    eduoffer_status = forms.MultipleChoiceField(label=FieldEducationalOfferFilter.STATUS, required=False,
                                                             choices=EDUOFFER_STATUSES,
                                                             widget=autocomplete.Select2Multiple(attrs={'class': 'select2'}))
    eduoffer_only_my = forms.BooleanField(label=FieldEducationalOfferFilter.ONLY_MY, required=False)     
        
    class Meta:
        model = EducationalOffer
        fields = ('eduoffer_status', 'eduoffer_only_my')


class EducationalOfferFilter(django_filters.FilterSet):
    eduoffer_institution = django_filters.ModelChoiceFilter(label=FieldEducationalOffer.INSTITUTION,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='institution-autocomplete'))
    eduoffer_position_text = django_filters.CharFilter(label=FieldEducationalOffer.POSITION, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    eduoffer_type = django_filters.ModelMultipleChoiceFilter(label=FieldEducationalOffer.TYPE,
                                                             queryset=EducationalOfferType.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='educationaloffertype-autocomplete'))
    eduoffer_mode = django_filters.ModelMultipleChoiceFilter(label=FieldEducationalOffer.MODE,
                                                             queryset=EducationalOfferMode.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='educationaloffermode-autocomplete'))
    eduoffer_city__region = django_filters.ModelChoiceFilter(label=FieldEducationalOffer.REGION,
                                                             queryset=Region.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='region-autocomplete'))
    eduoffer_city = django_filters.ModelChoiceFilter(label=FieldEducationalOffer.CITY,
                                                             queryset=City.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='city-autocomplete'))
    eduoffer_date_start = django_filters.DateFilter(label=FieldEducationalOffer.DATE_START, lookup_expr='gte', widget=forms.DateInput(attrs={'class': 'datepicker list__form--input'}))
    eduoffer_date_end = django_filters.DateFilter(label=FieldEducationalOffer.DATE_END, lookup_expr='lte', widget=forms.DateInput(attrs={'class': 'datepicker list__form--input'}))
    eduoffer_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldEducationalOffer.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    eduoffer_is_accepted = django_filters.BooleanFilter(label=FieldEducationalOffer.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))    

    o = django_filters.OrderingFilter(
        fields=(
            ('eduoffer_is_promoted', 'eduoffer_is_promoted'),
            ('eduoffer_date_add', 'eduoffer_date_add'),
            ('eduoffer_position_text', 'eduoffer_position_text'),
            ('eduoffer_date_end', 'eduoffer_date_end'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = EducationalOffer
        form = EducationalOfferFilterForm
        fields = ['eduoffer_institution', 'eduoffer_position_text',
                  'eduoffer_type', 'eduoffer_mode',
                  'eduoffer_city__region', 'eduoffer_city',
                  'eduoffer_date_start', 'eduoffer_date_end',
                  'eduoffer_keywords', 'eduoffer_is_accepted']
