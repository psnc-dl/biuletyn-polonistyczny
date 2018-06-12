# -*- coding: utf-8 -*-
from django import forms
from haystack.forms import ModelSearchForm, model_choices
from .fields import FieldSearchForm


class SearchForm(ModelSearchForm):
    
    def __init__(self, *args, **kwargs):
        super(ModelSearchForm, self).__init__(*args, **kwargs)
        self.fields['models'] = forms.MultipleChoiceField(choices=model_choices(), required=False, label=FieldSearchForm.SEARCH_IN, widget=forms.CheckboxSelectMultiple)    
        
        