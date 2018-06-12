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

from .filters import NewFilter
from .forms import NewForm, ConfirmNewForm, NewFileInline, NewLinkInline, NewContentContributionInline
from .messages import MessageNew
from .models import New, NewAuthorized, NewModification
from .permissions import check_new_write_permission, check_new_read_permission


def new_query(request):
    GET = request.GET.copy()

    new_only_my = GET.get('new_only_my')

    user = request.user
    filter_args = [];
    published = Q(new_is_accepted=True)
    owner = Q(new_added_by=user)
    modif = Q(new_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(new_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)

    if new_only_my:
        only_my = Q(new_added_by=user)
        filter_args.append(only_my)

    # distinct because of many new_authorizations that give duplicates in joins
    qset = New.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET]        


def new_filtering(request):
    query_result = new_query(request)
    qset = query_result[0]
    GET = query_result[2]
    
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-new_date_add'
        o = GET.get('o')
        
    f = NewFilter(GET, queryset=qset)
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

    
def new_list(request):
    response_dict, _ = new_filtering(request)
    return render_to_response('bportal_modules/details/news/list.html', response_dict, RequestContext(request))


def new_pdf(request):
    new_id = request.GET['new_id']
    template_name = "bportal_modules/details/news/details_pdf.html"
    new = New.objects.get(new_id=new_id)
    context = {"new": new, }
    return pdf.generateHttpResponse(request, context, template_name)


def new_list_pdf(request):
    template_name = "bportal_modules/details/news/list_pdf.html"
    query_result, _ = new_filtering(request)           
    context = {"news": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def new_csv(request):
    query_result, _ = new_filtering(request)     
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="news.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.new_title_text, q.new_category.new_category_item_name])
    return response


class NewDetailView(DetailView):
    model = New
    template_name = 'bportal_modules/details/news/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'new_title_slug'
    query_pk_and_slug = True
    
    def get_object(self, *args, **kwargs):     
        new = super(NewDetailView, self).get_object(*args, **kwargs)
            
        response_dict, new.curr_page = new_filtering(self.request)
        new.filter = response_dict['filter'] if 'filter' in response_dict else None
        new.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
                
        return check_new_read_permission(self.request.user, new)
    
    def get_context_data(self, **kwargs):
        context = super(NewDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context


class NewCreateView(CreateWithInlinesView, ChangeMessageView):
    model = New
    form_class = NewForm
    inlines = [NewFileInline, NewLinkInline, NewContentContributionInline]
    template_name = 'bportal_modules/details/news/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            title = request.POST['new_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = New.objects.filter(new_title_text=title)  
            if dup_list:         
                if (self.form_class is not ConfirmNewForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageNew.DUPLICATE)
                else:
                    self.form_class = NewForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(NewCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmNewForm if self.duplicate else self.form_class

    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.new_added_by = user
        form.instance.new_modified_by = user
        form.instance.new_title = remove_unnecessary_tags_from_title(form.instance.new_title)
        form.instance.new_title_text = strip_tags(form.instance.new_title)        
        form.instance.new_title_slug = slugify_text_title(form.instance.new_title_text)

        response = super(NewCreateView, self).forms_valid(form, inlines)
        
        modification = NewModification.objects.create(new=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            NewAuthorized.objects.create(new=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)
        
        return response


class NewUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = New
    form_class = NewForm
    inlines = [NewFileInline, NewLinkInline, NewContentContributionInline]
    template_name = 'bportal_modules/details/news/edit.html'
    pk_url_kwarg = 'id'    
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        new = super(NewUpdateView, self).get_object(*args, **kwargs)
        return check_new_write_permission(self.request.user, new)
    
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.new_modified_by = user
        form.instance.new_date_edit = timezone.now()
        form.instance.new_title = remove_unnecessary_tags_from_title(form.instance.new_title)
        form.instance.new_title_text = strip_tags(form.instance.new_title)       
        form.instance.new_title_slug = slugify_text_title(form.instance.new_title_text)        

        response = super(NewUpdateView, self).forms_valid(form, inlines)

        modification = NewModification.objects.create(new=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)
        
        return response


class NewDeleteView(generic.DeleteView):
    model = New
    template_name = 'bportal_modules/details/news/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('new_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        new = super(NewDeleteView, self).get_object(*args, **kwargs)
        return check_new_write_permission(self.request.user, new)
