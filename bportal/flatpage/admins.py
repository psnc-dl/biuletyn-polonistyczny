# -*- coding: utf-8 -*-
from .forms import FlatPageForm
from django.contrib.flatpages.admin import FlatPageAdmin

class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageForm
