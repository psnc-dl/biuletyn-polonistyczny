# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import JobOfferDiscipline, JobOfferType, JobOffer


class JobOfferDisciplineAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = JobOfferDiscipline.objects.all()
        if self.q:
            qs = qs.filter(discipline_name__istartswith=self.q)
        return qs


class JobOfferTypeAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = JobOfferType.objects.all()
        if self.q:
            qs = qs.filter(type_name__istartswith=self.q)
        return qs


class JobOfferAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = JobOffer.objects.all()
        if self.q:
            qs = qs.filter(joboffer_position_text__istartswith=self.q)
        return qs

