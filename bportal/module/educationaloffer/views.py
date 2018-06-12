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

from .filters import EducationalOfferFilter, EducationalOfferFilterForm
from .forms import EducationalOfferForm, ConfirmEducationalOfferForm, EducationalOfferFileInline, EducationalOfferLinkInline, EducationalOfferContentContributionInline
from .messages import MessageEducationalOffer
from .models import EducationalOffer, EducationalOfferAuthorized, EducationalOfferModification
from .permissions import check_eduoffer_write_permission, check_eduoffer_read_permission


def educationaloffer_query(request):
    GET = request.GET.copy()

    eduoffer_status = GET.getlist('eduoffer_status')
    if not eduoffer_status:
        GET.setlist('eduoffer_status', [EducationalOfferFilterForm.EDUOFFER_STATUS_IN_PROGRESS, EducationalOfferFilterForm.EDUOFFER_STATUS_FINISHED])
        eduoffer_status = GET.getlist('eduoffer_status')
    
    eduoffer_only_my = GET.get('eduoffer_only_my')
        
    user = request.user
    filter_args = [];
    published = Q(eduoffer_is_accepted=True)
    owner = Q(eduoffer_added_by=user)
    modif = Q(eduoffer_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(eduoffer_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)
        
    if not (EducationalOfferFilterForm.EDUOFFER_STATUS_FINISHED in eduoffer_status and EducationalOfferFilterForm.EDUOFFER_STATUS_IN_PROGRESS in eduoffer_status):
        if EducationalOfferFilterForm.EDUOFFER_STATUS_FINISHED in eduoffer_status:
            finished = Q(eduoffer_date_end__lt=timezone.now().date())
            filter_args.append(finished)    
        if EducationalOfferFilterForm.EDUOFFER_STATUS_IN_PROGRESS in eduoffer_status:
            inprogress = Q(eduoffer_date_end__gte=timezone.now().date())
            unknown = Q(eduoffer_date_end__isnull=True)
            filter_args.append(inprogress | unknown)        

    if eduoffer_only_my:
        only_my = Q(eduoffer_added_by=user)
        filter_args.append(only_my)

    # distinct because of many eduoffer_authorizations that give duplicates in joins
    qset = EducationalOffer.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET]    


def educationaloffer_filtering(request):
    query_result = educationaloffer_query(request)
    qset = query_result[0]
    GET = query_result[2]    
    
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-eduoffer_is_promoted,-eduoffer_date_add'
        o = GET.get('o')     
            
    f = EducationalOfferFilter(GET, queryset=qset)
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


def educationaloffer_list(request):
    response_dict, _ = educationaloffer_filtering(request)
    return render_to_response('bportal_modules/details/educationaloffers/list.html', response_dict, RequestContext(request))

     
def educationaloffer_pdf(request):
    eduoffer_id = request.GET['eduoffer_id']
    template_name = "bportal_modules/details/educationaloffers/details_pdf.html"
    eduoffer = EducationalOffer.objects.get(eduoffer_id=eduoffer_id)
    context = RequestContext(request, {"eduoffer": eduoffer, })
    return pdf.generateHttpResponse(request, context, template_name)


def educationaloffer_list_pdf(request):
    template_name = "bportal_modules/details/educationaloffers/list_pdf.html"
    query_result, _ = educationaloffer_filtering(request)      
    context = {"eduoffers": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def educationaloffer_csv(request):
    query_result, _ = educationaloffer_filtering(request)         
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="educationaloffers.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.eduoffer_position_text, q.eduoffer_mode, q.eduoffer_date_end, q.eduoffer_institution])
    return response

     
class EducationalOfferDetailView(DetailView):
    model = EducationalOffer
    template_name = 'bportal_modules/details/educationaloffers/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'eduoffer_position_slug'
    query_pk_and_slug = True    
        
    def get_object(self, *args, **kwargs):     
        eduoffer = super(EducationalOfferDetailView, self).get_object(*args, **kwargs)

        response_dict, eduoffer.curr_page = educationaloffer_filtering(self.request)
        eduoffer.filter = response_dict['filter'] if 'filter' in response_dict else None
        eduoffer.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
        
        return check_eduoffer_read_permission(self.request.user, eduoffer)
    
    def get_context_data(self, **kwargs):
        context = super(EducationalOfferDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context


class EducationalOfferCreateView(CreateWithInlinesView, ChangeMessageView):
    model = EducationalOffer
    form_class = EducationalOfferForm
    inlines = [EducationalOfferFileInline, EducationalOfferLinkInline, EducationalOfferContentContributionInline]
    template_name = 'bportal_modules/details/educationaloffers/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try:
            position = request.POST['eduoffer_position']
            position = remove_unnecessary_tags_from_title(position)
            position = strip_tags(position)
            dup_list = EducationalOffer.objects.filter(eduoffer_position_text=position)  
            if dup_list:         
                if (self.form_class is not ConfirmEducationalOfferForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageEducationalOffer.DUPLICATE)
                else:
                    self.form_class = EducationalOfferForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(EducationalOfferCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmEducationalOfferForm if self.duplicate else self.form_class
    
    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.eduoffer_added_by = user
        form.instance.eduoffer_modified_by = user
        form.instance.eduoffer_position = remove_unnecessary_tags_from_title(form.instance.eduoffer_position)
        form.instance.eduoffer_position_text = strip_tags(form.instance.eduoffer_position)
        form.instance.eduoffer_position_slug = slugify_text_title(form.instance.eduoffer_position_text)
        
        response = super(EducationalOfferCreateView, self).forms_valid(form, inlines)
        
        modification = EducationalOfferModification.objects.create(eduoffer=self.object, user=user, date_time=timezone.now())  
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            EducationalOfferAuthorized.objects.create(eduoffer=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)        
                
        return response
     
     
class EducationalOfferUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = EducationalOffer
    form_class = EducationalOfferForm
    inlines = [EducationalOfferFileInline, EducationalOfferLinkInline, EducationalOfferContentContributionInline]
    template_name = 'bportal_modules/details/educationaloffers/edit.html'
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EducationalOfferUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        eduoffer = super(EducationalOfferUpdateView, self).get_object(*args, **kwargs)
        return check_eduoffer_write_permission(self.request.user, eduoffer)
            
    def forms_valid(self, form, inlines):
        user = self.request.user 
        form.instance.eduoffer_modified_by = user
        form.instance.eduoffer_date_edit = timezone.now()
        form.instance.eduoffer_position = remove_unnecessary_tags_from_title(form.instance.eduoffer_position)
        form.instance.eduoffer_position_text = strip_tags(form.instance.eduoffer_position)
        form.instance.eduoffer_position_slug = slugify_text_title(form.instance.eduoffer_position_text)                 
        
        response = super(EducationalOfferUpdateView, self).forms_valid(form, inlines)
        
        modification = EducationalOfferModification.objects.create(eduoffer=self.object, user=user, date_time=timezone.now())  
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)
                
        return response
 
    
class EducationalOfferDeleteView(generic.DeleteView):
    model = EducationalOffer
    template_name = 'bportal_modules/details/educationaloffers/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('eduoffer_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EducationalOfferDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        eduoffer = super(EducationalOfferDeleteView, self).get_object(*args, **kwargs)
        return check_eduoffer_write_permission(self.request.user, eduoffer)    
    
