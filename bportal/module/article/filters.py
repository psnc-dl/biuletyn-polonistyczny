# -*- coding: utf-8 -*-
from dal import autocomplete
from django import forms
from django.forms.widgets import NullBooleanSelect
import django_filters
from taggit.models import Tag

from .fields import FieldArticle, FieldArticleFilter
from .models import  Article
from bportal.module.article.fields import FieldArticleContentContribution
from bportal.module.person.models import Person


class ArticleFilterForm(forms.ModelForm):
    article_only_my = forms.BooleanField(label=FieldArticleFilter.ONLY_MY, required=False) 
        
    class Meta:
        model = Article
        fields = ('article_only_my',)
       

class ArticleFilter(django_filters.FilterSet):
    article_title_text = django_filters.CharFilter(label=FieldArticle.TITLE, lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'list__form--input'}))
    article_keywords = django_filters.ModelMultipleChoiceFilter(label=FieldArticle.KEYWORDS,
                                                             queryset=Tag.objects.all(),
                                                             widget=autocomplete.ModelSelect2Multiple(url='tag-autocomplete'))
    article_is_accepted = django_filters.BooleanFilter(label=FieldArticle.IS_ACCEPTED,
                                                             widget=NullBooleanSelect(attrs={'class': 'select2'}))
    article_contributors = django_filters.ModelChoiceFilter(label=FieldArticleContentContribution.PERSON,
                                                             queryset=Person.objects.all(),
                                                             widget=autocomplete.ModelSelect2(url='person-autocomplete'))  
    
    o = django_filters.OrderingFilter(
        fields=(
            ('article_date_add', 'article_date_add'),
            ('article_is_promoted', 'article_is_promoted'),
            ('article_title_text', 'article_title_text'),
        ),
    )    
        
    strict = True
    
    class Meta:
        model = Article
        form = ArticleFilterForm
        fields = ['article_title_text', 'article_contributors',
                  'article_keywords', 'article_is_accepted']
