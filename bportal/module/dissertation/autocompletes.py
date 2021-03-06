# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import Dissertation


class DissertationAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = Dissertation.objects.all()
        if self.q:
            qs = qs.filter(dissertation_title_text__istartswith=self.q)
        return qs

