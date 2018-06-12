# -*- coding: utf-8 -*-
from dal import autocomplete
from django.db.models import Q

from .models import ScientificTitle, Person


class ScientificTitleAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = ScientificTitle.objects.all()
        if self.q:
            qs = qs.filter(Q(scientific_title_abbreviation__istartswith=self.q) | Q(scientific_title_name__istartswith=self.q))
        return qs


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = Person.objects.all()
        if self.q:
            qs = qs.filter(Q(person_last_name__istartswith=self.q) | Q(person_first_name__istartswith=self.q))
        return qs
