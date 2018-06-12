# -*- coding: utf-8 -*-
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from bportal.module.common.models import PublicationCategory
from bportal.module.institution.models import Institution

from .fields import FieldJournalIssue, FieldJournalIssueFilter
from .models import Journal, JournalIssue


class JournalIssueFilterForm(forms.ModelForm):
    journalissue_only_my = forms.BooleanField(label=FieldJournalIssueFilter.ONLY_MY, required=False)    
    
    class Meta:
        model = JournalIssue
        fields = ('journalissue_only_my',)



class JournalIssueFilter(django_filters.FilterSet):
    journalissue_title_text = django_filters.CharFilter(label=FieldJournalIssue.TITLE, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    journalissue_publisher = django_filters.ModelChoiceFilter(label=FieldJournalIssue.PUBLISHERS,
                                                             queryset=Institution.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='institution-autocomplete'))    
    journalissue_category = django_filters.ModelMultipleChoiceFilter(label=FieldJournalIssue.CATEGORY,
                                                             queryset=PublicationCategory.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='publicationcategory-autocomplete'))
    journalissue_journal = django_filters.ModelMultipleChoiceFilter(label=FieldJournalIssue.JOURNAL,
                                                             queryset=Journal.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='journal-autocomplete'))
    journalissue_publication_date = django_filters.DateFilter(label=FieldJournalIssue.PUBLICATION_DATE, lookup_expr='exact', widget=forms.DateTimeInput(attrs={'class': 'datepicker list__form--input'}))
    journalissue_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldJournalIssue.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    journalissue_is_accepted = django_filters.BooleanFilter(label=FieldJournalIssue.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))
    
    o = django_filters.OrderingFilter(
        fields=(
            ('journalissue_is_promoted', 'journalissue_is_promoted'),
            ('journalissue_date_add', 'journalissue_date_add'),
            ('journalissue_title_text', 'journalissue_title_text'),
        ),
    )
    
    strict = True
    
    class Meta:
        model = JournalIssue
        form = JournalIssueFilterForm
        fields = ['journalissue_title_text', 'journalissue_publisher',
                'journalissue_category', 'journalissue_publication_date',
                'journalissue_keywords', 'journalissue_is_accepted']
