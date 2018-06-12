# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import Journal, JournalIssue


class JournalAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Journal.objects.all()
        if self.q:
            qs = qs.filter(journal_title_text__istartswith=self.q)
        return qs
    
class JournalIssueAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = JournalIssue.objects.all()
        if self.q:
            qs = qs.filter(journalissue_title_text__istartswith=self.q)
        return qs