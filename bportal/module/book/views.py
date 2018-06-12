# -*- coding: utf-8 -*-
import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import generic
from django.views.generic import DetailView
from extra_views import UpdateWithInlinesView, CreateWithInlinesView
import reversion

from bportal.account.profile.models import UserProfile
from bportal.account.profile.utils import UserConfig
from bportal.module.common import pdf
from bportal.module.common.permissions import has_create_permission
from bportal.module.common.utils import ExtendedPaginator
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title
from bportal.module.common.view import ChangeMessageView

from .filters import BookFilter
from .forms import BookForm, ConfirmBookForm, BookFileInline, BookLinkInline, BookContentContributionInline
from .messages import MessageBook
from .models import Book, BookAuthorized, BookModification
from .permissions import check_book_write_permission, check_book_read_permission


def book_query(request):
    GET = request.GET.copy()

    book_only_my = GET.get('book_only_my')

    user = request.user
    filter_args = [];
    published = Q(book_is_accepted=True)
    owner = Q(book_added_by=user)
    modif = Q(book_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(book_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)

    if book_only_my:
        only_my = Q(book_added_by=user)
        filter_args.append(only_my)

    # distinct because of many book_authorizations that give duplicates in joins 
    qset = Book.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET]        


def book_filtering(request):
    query_result = book_query(request)
    qset = query_result[0]
    GET = query_result[2]
    
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-book_is_promoted,-book_date_add'
        o = GET.get('o')
        
    f = BookFilter(GET, queryset=qset)
    per_page = UserConfig.getPerPage(request, GET)
    paginator = Paginator(f.qs, per_page)
    
    page = GET.get('page', None)
    if page is not None:
        page = int(page)
    else:
        page = 1
    try:
        p = paginator.page(page)
    except PageNotAnInteger:
        p = paginator.page(1)
    except EmptyPage:
        p = paginator.page(paginator.num_pages)
         
    response_dict = dict()
    response_dict['filter'] = f
    response_dict['curr_page'] = p
    response_dict['per_page'] = per_page
    response_dict['o'] = o
    response_dict['per_page_choices'] = UserConfig.perPageChoices()
    response_dict['pagination_prefix'] = ExtendedPaginator.construct_filter_string(f.data)
    
    return response_dict, page

    
def book_list(request):
    response_dict, _ = book_filtering(request)
    return render_to_response('bportal_modules/details/books/list.html', response_dict, RequestContext(request))


def book_pdf(request):
    book_id = request.GET['book_id']
    template_name = "bportal_modules/details/books/details_pdf.html"
    book = Book.objects.get(book_id=book_id)
    context = {"book": book, }
    return pdf.generateHttpResponse(request, context, template_name)


def book_list_pdf(request):
    template_name = "bportal_modules/details/books/list_pdf.html"
    query_result, _ = book_filtering(request)           
    context = {"books": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def book_csv(request):
    query_result, _ = book_filtering(request)     
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="books.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.book_title_text, q.book_category.publication_category_name, q.book_publisher])
    return response


class BookDetailView(DetailView):
    model = Book
    template_name = 'bportal_modules/details/books/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'book_title_slug'
    query_pk_and_slug = True
    
    def get_object(self, *args, **kwargs):     
        book = super(BookDetailView, self).get_object(*args, **kwargs)
            
        response_dict, book.curr_page = book_filtering(self.request)
        book.filter = response_dict['filter'] if 'filter' in response_dict else None
        book.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
                
        return check_book_read_permission(self.request.user, book)
    
    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context


class BookCreateView(CreateWithInlinesView, ChangeMessageView):
    model = Book
    form_class = BookForm
    inlines = [BookFileInline, BookLinkInline, BookContentContributionInline]
    template_name = 'bportal_modules/details/books/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            title = request.POST['book_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = Book.objects.filter(book_title_text=title)  
            if dup_list:         
                if (self.form_class is not ConfirmBookForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageBook.DUPLICATE)
                else:
                    self.form_class = BookForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(BookCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmBookForm if self.duplicate else self.form_class

    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.book_added_by = user
        form.instance.book_modified_by = user
        form.instance.book_title = remove_unnecessary_tags_from_title(form.instance.book_title)
        form.instance.book_title_text = strip_tags(form.instance.book_title)        
        form.instance.book_title_slug = slugify_text_title(form.instance.book_title_text)

        response = super(BookCreateView, self).forms_valid(form, inlines)
        
        modification = BookModification.objects.create(book=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            BookAuthorized.objects.create(book=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)        
        
        return response


class BookUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = Book
    form_class = BookForm
    inlines = [BookFileInline, BookLinkInline, BookContentContributionInline]
    template_name = 'bportal_modules/details/books/edit.html'
    pk_url_kwarg = 'id'    
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BookUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        book = super(BookUpdateView, self).get_object(*args, **kwargs)
        return check_book_write_permission(self.request.user, book)
    
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.book_modified_by = user
        form.instance.book_date_edit = timezone.now()
        form.instance.book_title = remove_unnecessary_tags_from_title(form.instance.book_title)
        form.instance.book_title_text = strip_tags(form.instance.book_title)       
        form.instance.book_title_slug = slugify_text_title(form.instance.book_title_text)        

        response = super(BookUpdateView, self).forms_valid(form, inlines)

        modification = BookModification.objects.create(book=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)
        
        return response


class BookDeleteView(generic.DeleteView):
    model = Book
    template_name = 'bportal_modules/details/books/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('book_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BookDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        book = super(BookDeleteView, self).get_object(*args, **kwargs)
        return check_book_write_permission(self.request.user, book)
