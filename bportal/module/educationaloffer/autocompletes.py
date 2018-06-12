# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import EducationalOfferMode, EducationalOfferType, EducationalOffer


class EducationalOfferModeAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = EducationalOfferMode.objects.all()
        if self.q:
            qs = qs.filter(mode_name__istartswith=self.q)
        return qs


class EducationalOfferTypeAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = EducationalOfferType.objects.all()
        if self.q:
            qs = qs.filter(type_name__istartswith=self.q)
        return qs   


class EducationalOfferAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = EducationalOffer.objects.all()
        if self.q:
            qs = qs.filter(eduoffer_position_text__istartswith=self.q)
        return qs   
