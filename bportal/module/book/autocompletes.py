# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import Book


class BookAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Book.objects.all()
        if self.q:
            qs = qs.filter(book_title_text__istartswith=self.q)
        return qs
