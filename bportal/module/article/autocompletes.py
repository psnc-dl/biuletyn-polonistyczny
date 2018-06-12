# -*- coding: utf-8 -*-
from dal import autocomplete

from .models import Article


class ArticleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Article.objects.all()
        if self.q:
            qs = qs.filter(article_title_text__istartswith=self.q)
        return qs
