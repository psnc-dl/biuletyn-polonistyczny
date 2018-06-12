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
from django.views.generic.detail import DetailView
from extra_views.advanced import CreateWithInlinesView, UpdateWithInlinesView
import reversion

from bportal.account.profile.models import UserProfile
from bportal.account.profile.utils import UserConfig
from bportal.module.common import pdf
from bportal.module.common.permissions import has_create_permission
from bportal.module.common.utils import ExtendedPaginator
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title
from bportal.module.common.view import ChangeMessageView

from .filters import JobOfferFilter, JobOfferFilterForm
from .forms import JobOfferForm, ConfirmJobOfferForm, JobOfferFileInline, JobOfferLinkInline, JobOfferContentContributionInline
from .messages import MessageJobOffer
from .models import JobOffer, JobOfferAuthorized, JobOfferModification
from .permissions import check_joboffer_write_permission, check_joboffer_read_permission


def joboffer_query(request):
    GET = request.GET.copy()

    joboffer_status = GET.getlist('joboffer_status')
    if not joboffer_status:
        GET.setlist('joboffer_status', [JobOfferFilterForm.JOBOFFER_STATUS_IN_PROGRESS, JobOfferFilterForm.JOBOFFER_STATUS_FINISHED])
        joboffer_status = GET.getlist('joboffer_status')
   
    joboffer_only_my = GET.get('joboffer_only_my')
       
    user = request.user
    filter_args = [];
    published = Q(joboffer_is_accepted=True)
    owner = Q(joboffer_added_by=user)
    modif = Q(joboffer_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(joboffer_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)
        
    if not (JobOfferFilterForm.JOBOFFER_STATUS_FINISHED in joboffer_status and JobOfferFilterForm.JOBOFFER_STATUS_IN_PROGRESS in joboffer_status):
        if JobOfferFilterForm.JOBOFFER_STATUS_FINISHED in joboffer_status:
            finished = Q(joboffer_date_end__lt=timezone.now().date())
            filter_args.append(finished)    
        if JobOfferFilterForm.JOBOFFER_STATUS_IN_PROGRESS in joboffer_status:
            inprogress = Q(joboffer_date_end__gte=timezone.now().date())
            unknown = Q(joboffer_date_end__isnull=True)
            filter_args.append(inprogress | unknown)
            
    if joboffer_only_my:
        only_my = Q(joboffer_added_by=user)
        filter_args.append(only_my)
           
    # distinct because of many cities that give many regions and consequently duplicates in joins (moreover joboffer_authorizations gives duplicates)
    qset = JobOffer.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET]

    
def joboffer_filtering(request):
    query_result = joboffer_query(request)
    qset = query_result[0]
    GET = query_result[2]

    o = GET.get('o', None)
    if not o:
        GET['o'] = '-joboffer_is_promoted,-joboffer_date_add'
        o = GET.get('o')   
        
    f = JobOfferFilter(GET, queryset=qset)
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


def joboffer_list(request):
    response_dict, _ = joboffer_filtering(request)
    return render_to_response('bportal_modules/details/joboffers/list.html', response_dict, RequestContext(request))


def joboffer_pdf(request):
    joboffer_id = request.GET['joboffer_id']
    template_name = "bportal_modules/details/joboffers/details_pdf.html"
    joboffer = JobOffer.objects.get(joboffer_id=joboffer_id)
    context = {"joboffer": joboffer, }
    return pdf.generateHttpResponse(request, context, template_name)


def joboffer_list_pdf(request):
    template_name = "bportal_modules/details/joboffers/list_pdf.html"
    query_result, _ = joboffer_filtering(request)       
    context = {"joboffers": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def joboffer_csv(request):
    query_result, _ = joboffer_filtering(request)      
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="joboffers.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.joboffer_position_text, q.joboffer_date_add, [x.discipline_name for x in q.joboffer_disciplines.all()], q.joboffer_institution])
    return response


class JobOfferDetailView(DetailView):
    model = JobOffer
    template_name = 'bportal_modules/details/joboffers/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'joboffer_position_slug'
    query_pk_and_slug = True
    
    def get_object(self, *args, **kwargs):     
        joboffer = super(JobOfferDetailView, self).get_object(*args, **kwargs)

        response_dict, joboffer.curr_page = joboffer_filtering(self.request)
        joboffer.filter = response_dict['filter'] if 'filter' in response_dict else None
        joboffer.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
        
        return check_joboffer_read_permission(self.request.user, joboffer)
    
    def get_context_data(self, **kwargs):
        context = super(JobOfferDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context
    
 
class JobOfferCreateView(CreateWithInlinesView, ChangeMessageView):
    model = JobOffer
    form_class = JobOfferForm
    inlines = [JobOfferFileInline, JobOfferLinkInline, JobOfferContentContributionInline]
    template_name = 'bportal_modules/details/joboffers/create.html'
    duplicate = False
        
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            position = request.POST['joboffer_position']
            position = remove_unnecessary_tags_from_title(position)
            position = strip_tags(position)
            dup_list = JobOffer.objects.filter(joboffer_position_text=position)  
            if dup_list:         
                if (self.form_class is not ConfirmJobOfferForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageJobOffer.DUPLICATE)
                else:
                    self.form_class = JobOfferForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(JobOfferCreateView, self).dispatch(request, *args, **kwargs)
            
    def get_form_class(self):
        return ConfirmJobOfferForm if self.duplicate else self.form_class

    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.form_invalid(form)
        user = self.request.user
        form.instance.joboffer_added_by = user
        form.instance.joboffer_modified_by = user
        form.instance.joboffer_position = remove_unnecessary_tags_from_title(form.instance.joboffer_position)
        form.instance.joboffer_position_text = strip_tags(form.instance.joboffer_position)     
        form.instance.joboffer_position_slug = slugify_text_title(form.instance.joboffer_position_text)
        
        response = super(JobOfferCreateView, self).forms_valid(form, inlines)
    
        modification = JobOfferModification.objects.create(joboffer=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            JobOfferAuthorized.objects.create(joboffer=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()            
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)
        
        return response


class JobOfferUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = JobOffer
    form_class = JobOfferForm
    inlines = [JobOfferFileInline, JobOfferLinkInline, JobOfferContentContributionInline]
    template_name = 'bportal_modules/details/joboffers/edit.html'
    pk_url_kwarg = 'id'  
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JobOfferUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        joboffer = super(JobOfferUpdateView, self).get_object(*args, **kwargs)
        return check_joboffer_write_permission(self.request.user, joboffer)
    
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.joboffer_modified_by = user
        form.instance.joboffer_date_edit = timezone.now()
        form.instance.joboffer_position = remove_unnecessary_tags_from_title(form.instance.joboffer_position)
        form.instance.joboffer_position_text = strip_tags(form.instance.joboffer_position)
        form.instance.joboffer_position_slug = slugify_text_title(form.instance.joboffer_position_text)              
        
        response = super(JobOfferUpdateView, self).forms_valid(form, inlines)
        
        modification = JobOfferModification.objects.create(joboffer=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()

        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)

        return response
    
    
class JobOfferDeleteView(generic.DeleteView):
    model = JobOffer
    template_name = 'bportal_modules/details/joboffers/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('joboffer_list')
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JobOfferDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        joboffer = super(JobOfferDeleteView, self).get_object(*args, **kwargs)
        return check_joboffer_write_permission(self.request.user, joboffer)
    
    
