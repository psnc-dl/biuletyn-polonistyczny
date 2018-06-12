# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import NewCategory


class NewCategoryAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = NewCategory.objects.all()
        if self.q:
            qs = qs.filter(new_category_name__istartswith=self.q)
        return qs
