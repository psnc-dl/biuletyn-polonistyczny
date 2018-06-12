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

from .filters import JournalIssueFilter
from .forms import JournalIssueForm, ConfirmJournalIssueForm, JournalIssueFileInline, JournalIssueLinkInline, JournalIssueContentContributionInline
from .messages import MessageJournalIssue
from .models import JournalIssue, JournalIssueAuthorized, JournalIssueModification
from .permissions import check_journalissue_write_permission, check_journalissue_read_permission
from bportal.module.journal.models import Journal


def get_last_added_issues(request, journal):
    user = request.user
    filter_args = [];
    published = Q(journalissue_is_accepted=True)
    owner = Q(journalissue_added_by=user)
    modif = Q(journalissue_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(journalissue_authorizations=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)

    qset = JournalIssue.objects.filter(*filter_args).filter(journalissue_journal=journal).order_by('-journalissue_date_add')[:4]
    return qset.all()


def journalissue_query(request):
    GET = request.GET.copy()

    journalissue_only_my = GET.get('journalissue_only_my')

    user = request.user
    filter_args = [];
    published = Q(journalissue_is_accepted=True)
    owner = Q(journalissue_added_by=user)
    modif = Q(journalissue_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(journalissue_authorizations=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)

    if journalissue_only_my:
        only_my = Q(journalissue_added_by=user)
        filter_args.append(only_my)

    qset = JournalIssue.objects.filter(*filter_args)
    return [qset, filter_args, GET]        


def journalissue_filtering(request):
    query_result = journalissue_query(request)
    qset = query_result[0]
    GET = query_result[2]
    
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-journalissue_is_promoted,-journalissue_date_add'
        o = GET.get('o')
        
    f = JournalIssueFilter(GET, queryset=qset)
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


def journalissue_list(request):
    response_dict, _ = journalissue_filtering(request)
    return render_to_response('bportal_modules/details/journals/issues/list.html', response_dict, RequestContext(request))


def journalissue_pdf(request):
    journalissue_id = request.GET['journalissue_id']
    template_name = "bportal_modules/details/journals/issues/details_pdf.html"
    journalissue = JournalIssue.objects.get(journalissue_id=journalissue_id)
    context = {"journalissue": journalissue, }
    return pdf.generateHttpResponse(request, context, template_name)


def journalissue_list_pdf(request):
    template_name = "bportal_modules/details/journals/issues/list_pdf.html"
    query_result, _ = journalissue_filtering(request)           
    context = {"journalissues": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def journalissue_csv(request):
    query_result, _ = journalissue_filtering(request)     
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="journalissues.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.journalissue_title_text, q.journalissue_category.publication_category_name, q.journalissue_publisher])
    return response


class JournalIssueDetailView(DetailView):
    model = JournalIssue
    template_name = 'bportal_modules/details/journals/issues/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'journalissue_title_slug'
    query_pk_and_slug = True
    
    def get_object(self, *args, **kwargs):     
        journalissue = super(JournalIssueDetailView, self).get_object(*args, **kwargs)
            
        response_dict, journalissue.curr_page = journalissue_filtering(self.request)
        journalissue.filter = response_dict['filter'] if 'filter' in response_dict else None
        journalissue.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
                
        return check_journalissue_read_permission(self.request.user, journalissue)
    
    def get_context_data(self, **kwargs):
        context = super(JournalIssueDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        context['last_added_journalissues'] = get_last_added_issues(self.request, self.object.journalissue_journal)
        return context


class JournalIssueCreateView(CreateWithInlinesView, ChangeMessageView):
    model = JournalIssue
    form_class = JournalIssueForm
    inlines = [JournalIssueFileInline, JournalIssueLinkInline, JournalIssueContentContributionInline]
    template_name = 'bportal_modules/details/journals/issues/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            title = request.POST['journalissue_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = JournalIssue.objects.filter(journalissue_title_text=title)  
            if dup_list:         
                if (self.form_class is not ConfirmJournalIssueForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageJournalIssue.DUPLICATE)
                else:
                    self.form_class = JournalIssueForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(JournalIssueCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmJournalIssueForm if self.duplicate else self.form_class

    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.journalissue_added_by = user
        form.instance.journalissue_modified_by = user
        form.instance.journalissue_title = remove_unnecessary_tags_from_title(form.instance.journalissue_title)
        form.instance.journalissue_title_text = strip_tags(form.instance.journalissue_title)        
        form.instance.journalissue_title_slug = slugify_text_title(form.instance.journalissue_title_text)

        response = super(JournalIssueCreateView, self).forms_valid(form, inlines)
        
        modification = JournalIssueModification.objects.create(journalissue=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            JournalIssueAuthorized.objects.create(journalissue=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)        
        
        return response


class JournalIssueUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = JournalIssue
    form_class = JournalIssueForm
    inlines = [JournalIssueFileInline, JournalIssueLinkInline, JournalIssueContentContributionInline]
    template_name = 'bportal_modules/details/journals/issues/edit.html'
    pk_url_kwarg = 'id'    
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JournalIssueUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        journalissue = super(JournalIssueUpdateView, self).get_object(*args, **kwargs)
        return check_journalissue_write_permission(self.request.user, journalissue)
    
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.journalissue_modified_by = user
        form.instance.journalissue_date_edit = timezone.now()
        form.instance.journalissue_title = remove_unnecessary_tags_from_title(form.instance.journalissue_title)
        form.instance.journalissue_title_text = strip_tags(form.instance.journalissue_title)       
        form.instance.journalissue_title_slug = slugify_text_title(form.instance.journalissue_title_text)        

        response = super(JournalIssueUpdateView, self).forms_valid(form, inlines)

        modification = JournalIssueModification.objects.create(journalissue=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)        
        
        return response


class JournalIssueDeleteView(generic.DeleteView):
    model = JournalIssue
    template_name = 'bportal_modules/details/journals/issues/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('journalissue_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JournalIssueDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        journalissue = super(JournalIssueDeleteView, self).get_object(*args, **kwargs)
        return check_journalissue_write_permission(self.request.user, journalissue)


class JournalDetailView(generic.DetailView):
    model = Journal
    template_name = 'bportal_modules/details/journals/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'journal_title_slug'
    query_pk_and_slug = True
    
    def get_context_data(self, **kwargs):
        context = super(JournalDetailView, self).get_context_data(**kwargs)
        context['last_added_issues'] = get_last_added_issues(self.request, self.object)
        return context
    