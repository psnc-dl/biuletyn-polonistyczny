# -*- coding: utf-8 -*-
from haystack.generic_views import SearchView
from .forms import SearchForm

class SearchView(SearchView):
    form_class = SearchForm

    

