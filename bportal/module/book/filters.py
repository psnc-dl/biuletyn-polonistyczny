# -*- coding: utf-8 -*-
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.common.models import PublicationCategory
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person

from .fields import FieldBook, FieldBookFilter
from .models import Book


class BookFilterForm(forms.ModelForm):
    book_only_my = forms.BooleanField(label=FieldBookFilter.ONLY_MY, required=False)    
    
    class Meta:
        model = Book
        fields = ('book_only_my',)



class BookFilter(django_filters.FilterSet):
    book_title_text = django_filters.CharFilter(label=FieldBook.TITLE, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    book_authors = django_filters.ModelChoiceFilter(label=FieldBook.AUTHORS,
                                                             queryset=Person.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='person-autocomplete'))
    book_publisher = django_filters.ModelChoiceFilter(label=FieldBook.PUBLISHERS,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='institution-autocomplete'))    
    book_category = django_filters.ModelMultipleChoiceFilter(label=FieldBook.CATEGORIES,
                                                             queryset=PublicationCategory.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='publicationcategory-autocomplete'))
    book_publication_date = django_filters.DateFilter(label=FieldBook.PUBLICATION_DATE, lookup_expr='exact', widget=forms.DateTimeInput(attrs={'class': 'datepicker list__form--input'}))
    book_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldBook.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    book_is_accepted = django_filters.BooleanFilter(label=FieldBook.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))
    
    o = django_filters.OrderingFilter(
        fields=(
            ('book_is_promoted', 'book_is_promoted'),
            ('book_date_add', 'book_date_add'),
            ('book_title_text', 'book_title_text'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = Book
        form = BookFilterForm
        fields = ['book_title_text', 'book_authors',
                  'book_publisher', 'book_category',
                  'book_publication_date', 'book_keywords',
                  'book_is_accepted']
