# -*- coding: utf-8 -*-
from django.views import generic

from .models import Institution


class InstitutionDetailView(generic.DetailView):
    model = Institution
    template_name = 'bportal_modules/details/institutions/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'institution_slug'
    query_pk_and_slug = True
