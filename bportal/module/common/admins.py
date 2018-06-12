# -*- coding: utf-8 -*-
from django.contrib import admin


class TargetGroupAdmin(admin.ModelAdmin):
    list_display = ('target_name',)

class ResearchDisciplineAdmin(admin.ModelAdmin):
    list_display = ('discipline_fullname',)

class PublicationCategoryAdmin(admin.ModelAdmin):
    list_display = ('publication_category_name',)
