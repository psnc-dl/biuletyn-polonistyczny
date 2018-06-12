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
from extra_views import UpdateWithInlinesView, CreateWithInlinesView
import reversion

from bportal.account.profile.models import UserProfile
from bportal.account.profile.utils import UserConfig
from bportal.module.common import pdf
from bportal.module.common.permissions import has_create_permission
from bportal.module.common.utils import ExtendedPaginator
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title
from bportal.module.common.view import ChangeMessageView

from .filters import ScholarshipFilter, ScholarshipFilterForm
from .forms import ScholarshipForm, ConfirmScholarshipForm, ScholarshipFileInline, ScholarshipLinkInline, ScholarshipContentContributionInline
from .messages import MessageScholarship
from .models import Scholarship, ScholarshipAuthorized, ScholarshipModification
from .permissions import check_scholarship_write_permission, check_scholarship_read_permission


def scholarship_query(request):
    GET = request.GET.copy()

    scholarship_status = GET.getlist('scholarship_status')
    if not scholarship_status:
        GET.setlist('scholarship_status', [ScholarshipFilterForm.SCHOLARSHIP_STATUS_IN_PROGRESS, ScholarshipFilterForm.SCHOLARSHIP_STATUS_FINISHED])
        scholarship_status = GET.getlist('scholarship_status')    
    
    scholarship_only_my = GET.get('scholarship_only_my')    
    
    user = request.user
    filter_args = [];
    published = Q(scholarship_is_accepted=True)
    owner = Q(scholarship_added_by=user)
    modif = Q(scholarship_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(scholarship_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)
        
    if not (ScholarshipFilterForm.SCHOLARSHIP_STATUS_FINISHED in scholarship_status and ScholarshipFilterForm.SCHOLARSHIP_STATUS_IN_PROGRESS in scholarship_status):
        if ScholarshipFilterForm.SCHOLARSHIP_STATUS_FINISHED in scholarship_status:
            finished = Q(scholarship_date_end__lt=timezone.now().date())
            filter_args.append(finished)    
        if ScholarshipFilterForm.SCHOLARSHIP_STATUS_IN_PROGRESS in scholarship_status:
            inprogress = Q(scholarship_date_end__gte=timezone.now().date())
            unknown = Q(scholarship_date_end__isnull=True)
            filter_args.append(inprogress | unknown)

    if scholarship_only_my:
        only_my = Q(scholarship_added_by=user)
        filter_args.append(only_my)

    # distinct because of many scholarship_authorizations that give duplicates in joins
    qset = Scholarship.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET]  


def scholarship_filtering(request):
    query_result = scholarship_query(request)
    qset = query_result[0]
    GET = query_result[2]    
            
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-scholarship_is_promoted,-scholarship_date_add'
        o = GET.get('o')        
        
    f = ScholarshipFilter(GET, queryset=qset)
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


def scholarship_list(request):
    response_dict, _ = scholarship_filtering(request)                     
    return render_to_response('bportal_modules/details/scholarships/list.html', response_dict, RequestContext(request))


def scholarship_pdf(request):
    scholarship_id = request.GET['scholarship_id']
    template_name = "bportal_modules/details/scholarships/details_pdf.html"
    scholarship = Scholarship.objects.get(scholarship_id=scholarship_id)
    context = {"scholarship": scholarship, }
    return pdf.generateHttpResponse(request, context, template_name)


def scholarship_list_pdf(request):
    template_name = "bportal_modules/details/scholarships/list_pdf.html"
    query_result, _ = scholarship_filtering(request)    
    context = {"scholarships": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def scholarship_csv(request):
    query_result, _ = scholarship_filtering(request)        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scholarships.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.scholarship_name_text, q.scholarship_date_start, q.scholarship_type, q.scholarship_founder])
    return response


class ScholarshipDetailView(DetailView):
    model = Scholarship
    template_name = 'bportal_modules/details/scholarships/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'scholarship_name_slug'
    query_pk_and_slug = True    
        
    def get_object(self, *args, **kwargs):     
        scholarship = super(ScholarshipDetailView, self).get_object(*args, **kwargs)
        
        response_dict, scholarship.curr_page = scholarship_filtering(self.request)
        scholarship.filter = response_dict['filter'] if 'filter' in response_dict else None
        scholarship.per_page = response_dict['per_page'] if 'per_page' in response_dict else None

        return check_scholarship_read_permission(self.request.user, scholarship)
    
    def get_context_data(self, **kwargs):
        context = super(ScholarshipDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context


class ScholarshipCreateView(CreateWithInlinesView, ChangeMessageView):
    model = Scholarship
    form_class = ScholarshipForm
    inlines = [ScholarshipFileInline, ScholarshipLinkInline, ScholarshipContentContributionInline]
    template_name = 'bportal_modules/details/scholarships/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            name = request.POST['scholarship_name']
            name = remove_unnecessary_tags_from_title(name)
            name = strip_tags(name)            
            dup_list = Scholarship.objects.filter(scholarship_name_text=name)  
            if dup_list:         
                if (self.form_class is not ConfirmScholarshipForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageScholarship.DUPLICATE)
                else:
                    self.form_class = ScholarshipForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(ScholarshipCreateView, self).dispatch(request, *args, **kwargs)
       
    def get_form_class(self):
        return ConfirmScholarshipForm if self.duplicate else self.form_class
    
    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.form_invalid(form)
        user = self.request.user
        form.instance.scholarship_added_by = user
        form.instance.scholarship_modified_by = user
        form.instance.scholarship_name = remove_unnecessary_tags_from_title(form.instance.scholarship_name)
        form.instance.scholarship_name_text = strip_tags(form.instance.scholarship_name)         
        form.instance.scholarship_name_slug = slugify_text_title(form.instance.scholarship_name_text)        
        
        response = super(ScholarshipCreateView, self).forms_valid(form, inlines)
        
        modification = ScholarshipModification.objects.create(scholarship=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            ScholarshipAuthorized.objects.create(scholarship=self.object, authorized=institution)        
        profile.user_last_edit_date_time = modification.date_time
        profile.save()

        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message) 
        
        return response
        

class ScholarshipUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = Scholarship
    form_class = ScholarshipForm
    inlines = [ScholarshipFileInline, ScholarshipLinkInline, ScholarshipContentContributionInline]
    template_name = 'bportal_modules/details/scholarships/edit.html'
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ScholarshipUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        scholarship = super(ScholarshipUpdateView, self).get_object(*args, **kwargs)
        return check_scholarship_write_permission(self.request.user, scholarship)
    
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.scholarship_modified_by = user
        form.instance.scholarship_date_edit = timezone.now()
        form.instance.scholarship_name = remove_unnecessary_tags_from_title(form.instance.scholarship_name)
        form.instance.scholarship_name_text = strip_tags(form.instance.scholarship_name)  
        form.instance.scholarship_name_slug = slugify_text_title(form.instance.scholarship_name_text)              
        
        response = super(ScholarshipUpdateView, self).forms_valid(form, inlines)
        
        modification = ScholarshipModification.objects.create(scholarship=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()        

        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message) 

        return response
 

class ScholarshipDeleteView(generic.DeleteView):
    model = Scholarship
    template_name = 'bportal_modules/details/scholarships/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('scholarship_list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ScholarshipDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        scholarship = super(ScholarshipDeleteView, self).get_object(*args, **kwargs)
        return check_scholarship_write_permission(self.request.user, scholarship)
        
