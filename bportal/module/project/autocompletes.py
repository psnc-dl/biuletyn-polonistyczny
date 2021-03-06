# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import Project


class ProjectAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = Project.objects.all()
        if self.q:
            qs = qs.filter(project_title_text__istartswith=self.q)
        return qs

