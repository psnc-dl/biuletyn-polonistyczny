# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import ScholarshipType, Scholarship


class ScholarshipTypeAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = ScholarshipType.objects.all()
        if self.q:
            qs = qs.filter(type_name__istartswith=self.q)
        return qs


class ScholarshipAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = Scholarship.objects.all()
        if self.q:
            qs = qs.filter(tscholarship_name_text__istartswith=self.q)
        return qs
