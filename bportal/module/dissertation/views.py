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
from extra_views.advanced import CreateWithInlinesView, UpdateWithInlinesView
import reversion

from bportal.account.profile.models import UserProfile
from bportal.account.profile.utils import UserConfig
from bportal.module.common import pdf
from bportal.module.common.permissions import has_create_permission
from bportal.module.common.utils import ExtendedPaginator
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title
from bportal.module.common.view import ChangeMessageView

from .filters import DissertationFilter, DissertationFilterForm
from .forms import DissertationForm, ConfirmDissertationForm, DissertationFileInline, DissertationLinkInline, DissertationContentContributionInline
from .messages import MessageDissertation
from .models import Dissertation, DissertationAuthorized, DissertationModification
from .permissions import check_dissertation_write_permission, check_dissertation_read_permission


def dissertation_query(request):
    GET = request.GET.copy()

    dissertation_status = GET.getlist('dissertation_status')
    if not dissertation_status:
        GET.setlist('dissertation_status', [DissertationFilterForm.DISSERTATION_STATUS_IN_PROGRESS, DissertationFilterForm.DISSERTATION_STATUS_FINISHED])
        dissertation_status = GET.getlist('dissertation_status')

    dissertation_only_my = GET.get('dissertation_only_my')
    
    user = request.user
    filter_args = []
    published = Q(dissertation_is_accepted=True)
    owner = Q(dissertation_added_by=user)
    modif = Q(dissertation_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(dissertation_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)
        
    if not (DissertationFilterForm.DISSERTATION_STATUS_FINISHED in dissertation_status and DissertationFilterForm.DISSERTATION_STATUS_IN_PROGRESS in dissertation_status):
        if DissertationFilterForm.DISSERTATION_STATUS_FINISHED in dissertation_status:
            finished = Q(dissertation_date_end__lt=timezone.now().date())
            filter_args.append(finished)    
        if DissertationFilterForm.DISSERTATION_STATUS_IN_PROGRESS in dissertation_status:
            inprogress = Q(dissertation_date_end__gte=timezone.now().date())
            unknown = Q(dissertation_date_end__isnull=True)
            filter_args.append(inprogress | unknown) 

    if dissertation_only_my:
        only_my = Q(dissertation_added_by=user)
        filter_args.append(only_my)
  
    # distinct because of many dissertation_authorizations that give duplicates in joins
    qset = Dissertation.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET] 


def dissertation_filtering(request):
    query_result = dissertation_query(request)
    qset = query_result[0]
    GET = query_result[2]  
   
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-dissertation_is_promoted,-dissertation_date_add'
        o = GET.get('o')    
        
    f = DissertationFilter(GET, queryset=qset)
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


def dissertation_list(request):
    response_dict, _ = dissertation_filtering(request)                
    return render_to_response('bportal_modules/details/dissertations/list.html', response_dict, RequestContext(request))


def dissertation_pdf(request):
    dissertation_id = request.GET['dissertation_id']
    template_name = "bportal_modules/details/dissertations/details_pdf.html"
    dissertation = Dissertation.objects.get(dissertation_id=dissertation_id)
    context = {"dissertation": dissertation, }
    return pdf.generateHttpResponse(request, context, template_name)


def dissertation_list_pdf(request):
    template_name = "bportal_modules/details/dissertations/list_pdf.html"
    query_result, _ = dissertation_filtering(request)    
    context = {"dissertations": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def dissertation_csv(request):
    query_result, _ = dissertation_filtering(request)     
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dissertations.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.dissertation_title_text, q.dissertation_author.person_first_name + ' ' + q.dissertation_author.person_last_name, q.dissertation_date_start, q.dissertation_date_end, q.dissertation_institution])
    return response


class DissertationDetailView(generic.DetailView):
    model = Dissertation
    template_name = 'bportal_modules/details/dissertations/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'dissertation_title_slug'
    query_pk_and_slug = True        
    
    def get_object(self, *args, **kwargs):     
        dissertation = super(DissertationDetailView, self).get_object(*args, **kwargs)
      
        response_dict, dissertation.curr_page = dissertation_filtering(self.request)
        dissertation.filter = response_dict['filter'] if 'filter' in response_dict else None
        dissertation.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
            
        return check_dissertation_read_permission(self.request.user, dissertation)
    
    def get_context_data(self, **kwargs):
        context = super(DissertationDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context


class DissertationCreateView(CreateWithInlinesView, ChangeMessageView):
    model = Dissertation
    form_class = DissertationForm
    inlines = [DissertationFileInline, DissertationLinkInline, DissertationContentContributionInline]
    template_name = 'bportal_modules/details/dissertations/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            title = request.POST['dissertation_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = Dissertation.objects.filter(dissertation_title_text=title)  
            if dup_list:         
                if (self.form_class is not ConfirmDissertationForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageDissertation.DUPLICATE)
                else:
                    self.form_class = DissertationForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(DissertationCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmDissertationForm if self.duplicate else self.form_class
            
    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.dissertation_added_by = user
        form.instance.dissertation_modified_by = user
        form.instance.dissertation_title = remove_unnecessary_tags_from_title(form.instance.dissertation_title)
        form.instance.dissertation_title_text = strip_tags(form.instance.dissertation_title)
        form.instance.dissertation_title_slug = slugify_text_title(form.instance.dissertation_title_text)          
        
        response = super(DissertationCreateView, self).forms_valid(form, inlines)
        
        modification = DissertationModification.objects.create(dissertation=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            DissertationAuthorized.objects.create(dissertation=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()

        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)
                
        return response

                
class DissertationUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = Dissertation
    form_class = DissertationForm
    inlines = [DissertationFileInline, DissertationLinkInline, DissertationContentContributionInline]
    template_name = 'bportal_modules/details/dissertations/edit.html'
    pk_url_kwarg = 'id'
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DissertationUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        dissertation = super(DissertationUpdateView, self).get_object(*args, **kwargs)
        return check_dissertation_write_permission(self.request.user, dissertation)
                
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.dissertation_modified_by = user
        form.instance.dissertation_date_edit = timezone.now()
        form.instance.dissertation_title = remove_unnecessary_tags_from_title(form.instance.dissertation_title)
        form.instance.dissertation_title_text = strip_tags(form.instance.dissertation_title)
        form.instance.dissertation_title_slug = slugify_text_title(form.instance.dissertation_title_text)          
        
        response = super(DissertationUpdateView, self).forms_valid(form, inlines)
        
        modification = DissertationModification.objects.create(dissertation=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)
        
        return response


class DissertationDeleteView(generic.DeleteView):
    model = Dissertation
    template_name = 'bportal_modules/details/dissertations/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('dissertation_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DissertationDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        dissertation = super(DissertationDeleteView, self).get_object(*args, **kwargs)
        return check_dissertation_write_permission(self.request.user, dissertation)
