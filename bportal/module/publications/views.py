# -*- coding: utf-8 -*-
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from bportal.account.profile.models import UserProfile
from bportal.module.book.models import Book
from bportal.module.journal.models import JournalIssue

def publications_list(request):
    user = request.user
    
    # books
    books_filter_args = [];
    published = Q(book_is_accepted=True)
    owner = Q(book_added_by=user)
    modif = Q(book_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(book_authorizations__in=profile.user_institution.all())
            books_filter_args.append(published | owner | modif | inst)
    else:
        books_filter_args.append(published)    
    promoted_books = Book.objects.filter(book_is_promoted=True, *books_filter_args).order_by('-book_date_add')
    newest_books = Book.objects.filter(book_is_promoted=False, *books_filter_args).order_by('-book_date_add')[:10]
    
    # journals
    journalissues_filter_args = [];
    published = Q(journalissue_is_accepted=True)
    owner = Q(journalissue__added_by=user)
    modif = Q(journalissue_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(journalissue_authorizations__in=profile.user_institution.all())
            books_filter_args.append(published | owner | modif | inst)
    else:
        journalissues_filter_args.append(published)    
    promoted_journalissues = JournalIssue.objects.filter(journalissue_is_promoted=True, *journalissues_filter_args).order_by('-journalissue_date_add')
    newest_journalissues = JournalIssue.objects.filter(journalissue_is_promoted=False, *journalissues_filter_args).order_by('-journalissue_date_add')[:10]
    
    response_dict = dict()
    response_dict['promoted_books'] = promoted_books
    response_dict['newest_books'] = newest_books
    response_dict['promoted_journals'] = promoted_journalissues
    response_dict['newest_journals'] = newest_journalissues
    
    return render_to_response('bportal_modules/details/publications/list.html', response_dict, RequestContext(request))
