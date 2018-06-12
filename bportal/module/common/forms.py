# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _
from taggit.forms import TagWidget
from taggit.utils import parse_tags

from .fields import FieldBaseConfirm


class NoHistoryBooleanField(forms.BooleanField):
    
    def has_changed(self, initial, data):
        """
        Return that the field didn't change. It is used for the confirmation field.
        """
        return False
    

class BaseConfirmModelForm(forms.ModelForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False)
    


class HistoryTagField(forms.CharField):
    widget = TagWidget

    def __init__(self, max_length=None, min_length=None, strip=True, *args, **kwargs):
        self.max_length = max_length
        self.min_length = min_length
        self.strip = strip
        super(HistoryTagField, self).__init__(*args, **kwargs)


    def clean(self, value):
        value = super(HistoryTagField, self).clean(value)
        try:
            return parse_tags(value)
        except ValueError:
            raise forms.ValidationError(
                _("Please provide a comma-separated list of tags."))


    def has_changed(self, initial, data):
        """
        Return True if data differs from initial.
        """
        initial_set = set()
        for initial_object in initial:
            initial_set.add(initial_object.tag.name)
        data_set = set()
        if data:
            data_values = data.split(',')
            for data_value in data_values:
                data_set.add(data_value.strip())
        return initial_set != data_set
    