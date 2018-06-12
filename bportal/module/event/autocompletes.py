# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import Event, EventCategory


class EventCategoryAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = EventCategory.objects.all()
        if self.q:
            qs = qs.filter(event_category_name__istartswith=self.q)
        return qs


class EventAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Event.objects.all()
        if self.q:
            qs = qs.filter(event_name_text__istartswith=self.q)
        return qs   

