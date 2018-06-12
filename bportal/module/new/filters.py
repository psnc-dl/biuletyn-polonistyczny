# -*- coding: utf-8 -*-
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.person.models import Person

from .fields import FieldNew, FieldNewFilter
from .models import New, NewCategory


class NewFilterForm(forms.ModelForm):
    new_only_my = forms.BooleanField(label=FieldNewFilter.ONLY_MY, required=False)    
    
    class Meta:
        model = New
        fields = ('new_only_my',)



class NewFilter(django_filters.FilterSet):
    new_title_text = django_filters.CharFilter(label=FieldNew.TITLE, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    new_category = django_filters.ModelMultipleChoiceFilter(label=FieldNew.CATEGORIES,
                                                             queryset=NewCategory.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='newcategory-autocomplete'))
    new_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldNew.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    new_contributors = django_filters.ModelChoiceFilter(label=FieldNew.CONTRIBUTORS,
                                                             queryset=Person.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='person-autocomplete'))
    new_is_accepted = django_filters.BooleanFilter(label=FieldNew.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))
    
    o = django_filters.OrderingFilter(
        fields=(
            ('new_date_add', 'new_date_add'),
            ('new_title_text', 'new_title_text'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = New
        form = NewFilterForm
        fields = ['new_title_text', 'new_category', 
                  'new_keywords', 'new_contributors',
                  'new_is_accepted']
