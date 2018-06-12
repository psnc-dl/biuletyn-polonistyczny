# -*- coding: utf-8 -*-
from .models import InstitutionType, Institution
from dal import autocomplete
from django.db.models import Q


class InstitutionTypeAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = InstitutionType.objects.all()
        if self.q:
            qs = qs.filter(type_name__istartswith=self.q)
        return qs
    

class InstitutionAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = Institution.objects.all()
        if self.q:
            qs = qs.filter(Q(institution_fullname__istartswith=self.q) | Q(institution_shortname__istartswith=self.q))
        return qs
