# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import Competition


class CompetitionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Competition.objects.all()
        if self.q:
            qs = qs.filter(competition_title_text__istartswith=self.q)
        return qs

