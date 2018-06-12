# -*- coding: utf-8 -*-
from cities_light.models import City, Region, Country
from dal import autocomplete
from taggit.models import Tag

from .models import TargetGroup, ResearchDiscipline, PublicationCategory


class TargetGroupAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = TargetGroup.objects.all()
        if self.q:
            qs = qs.filter(target_name__istartswith=self.q)
        return qs


class ResearchDisciplineAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = ResearchDiscipline.objects.all()
        if self.q:
            qs = qs.filter(discipline_fullname__istartswith=self.q)
        return qs


class PublicationCategoryAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = PublicationCategory.objects.all()
        if self.q:
            qs = qs.filter(publication_category_name__istartswith=self.q)
        return qs


class CityAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = City.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

 
class RegionAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = Region.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

 
class CountryAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = Country.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

 
class TagAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        qs = Tag.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs
