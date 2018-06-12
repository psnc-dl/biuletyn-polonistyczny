# -*- coding: utf-8 -*-
import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
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

from .filters import EventFilter, EventFilterForm
from .forms import EventForm, EventFileInline, EventLinkInline, EventContentContributionInline, ConfirmEventModelForm, EventSummaryForm, EventSummaryPictureInline, EventSummaryFileInline, EventSummaryPublicationInline, EventSummaryLinkInline, EventSummaryContentContributionInline
from .messages import MessageEvent
from .models import Event, EventSummary, EventAuthorized, EventModification
from .permissions import check_event_write_permission, check_event_read_permission, has_event_write_permission, has_event_read_permission


def event_query(request):
    GET = request.GET.copy()

    event_status = GET.getlist('event_status')
    if not event_status:
        GET.setlist('event_status', [EventFilterForm.EVENT_STATUS_FURTHCOMING, EventFilterForm.EVENT_STATUS_IN_PROGRESS, EventFilterForm.EVENT_STATUS_PAST])
        event_status = GET.getlist('event_status')    
    
    event_only_my = GET.get('event_only_my')
        
    user = request.user
    filter_args = [];
    published = Q(event_is_accepted=True)
    owner = Q(event_added_by=user)
    modif = Q(event_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(event_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)

    status_args = [];
    if not (EventFilterForm.EVENT_STATUS_PAST in event_status and EventFilterForm.EVENT_STATUS_IN_PROGRESS in event_status and EventFilterForm.EVENT_STATUS_FURTHCOMING in event_status):
        if EventFilterForm.EVENT_STATUS_PAST in event_status:
            status_args.append(Q(event_date_from__lt=timezone.now().date()) & Q(event_date_to__isnull=True))
            status_args.append(Q(event_date_to__lt=timezone.now().date()) & Q(event_date_to__isnull=False))
        if EventFilterForm.EVENT_STATUS_IN_PROGRESS in event_status:
            status_args.append(Q(event_date_from=timezone.now().date()) & Q(event_date_to__isnull=True))
            status_args.append(Q(event_date_from__lte=timezone.now().date()) & Q(event_date_to__gte=timezone.now().date()) & Q(event_date_to__isnull=False))
        if EventFilterForm.EVENT_STATUS_FURTHCOMING in event_status:
            status_args.append(Q(event_date_from__gt=timezone.now().date()))
    if status_args:
        status_query = status_args.pop()
        for args in status_args:
            status_query |= args    
        filter_args.append(status_query)

    if event_only_my:
        only_my = Q(event_added_by=user)
        filter_args.append(only_my)

    # distinct because of many cities that give many regions and consequently duplicates in joins (moreover event_authorizations gives duplicates)
    qset = Event.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET]


def mark_closest_event(events_qs, position):
    if position >= 0 and position < len(events_qs):
        events_qs[position].is_closest = True        


def event_filtering(request, day_str=None):
    query_result = event_query(request)
    qset = query_result[0]
    filter_args = query_result[1]
    GET = query_result[2]  
    
    o = GET.get('o', None)
    if not o:
        GET['o'] = 'event_date_from,event_time_from'
        o = GET.get('o')     
        
    curr_day = timezone.now().date()
    if day_str is not None:
        curr_day = datetime.strptime(day_str, '%Y-%m-%d')
        
    f = EventFilter(GET, queryset=qset)
    per_page = UserConfig.getPerPage(request, GET)
    paginator = Paginator(f.qs, per_page)
    totalNoItems = f.qs.count()
   
    page = GET.get('page', None) 
    
    # calculate position of actual date page
    qdict = dict()
    qdict['event_date_from__gte'] = curr_day
    f2 = EventFilter(GET, queryset=qset.filter(*filter_args, **qdict))
    totalNoNewItems = f2.qs.count()
    diff = totalNoItems - totalNoNewItems
    position = diff % int(per_page)
    curr_date_page = diff // int(per_page) + 1
    
    # #if day then page was called from calendar
    if day_str:
        page = curr_date_page
        position = -1
        
    if page is None:
        page = curr_date_page
    else:
        page = int(page)
        # if selected page is different than curr_date_page, there is no event to mark as "is_closest"
        if page != curr_date_page:
            position = -1
        
    try:
        p = paginator.page(page)
    except PageNotAnInteger:
        p = paginator.page(1)
    except EmptyPage:
        p = paginator.page(paginator.num_pages)
    
    
    mark_closest_event(p, position) 
       
    response_dict = dict()
    response_dict['filter'] = f
    response_dict['curr_page'] = p
    response_dict['o'] = o
    response_dict['per_page'] = per_page
    response_dict['number_of_pages'] = paginator.num_pages
    response_dict['position'] = position
    response_dict['per_page_choices'] = UserConfig.perPageChoices()    
    response_dict['pagination_prefix'] = ExtendedPaginator.construct_filter_string(f.data)
    
    return response_dict, page 
   
    
def event_list(request):
    response_dict, _ = event_filtering(request)       
    return render_to_response('bportal_modules/details/events/list.html', response_dict, RequestContext(request))

def event_list_by_day(request, day=datetime.today()):
    _, page = event_filtering(request, day)
    return redirect(reverse('event_list') + '?page=' + str(page))


def event_pdf(request):
    event_id = request.GET['event_id']
    template_name = "bportal_modules/details/events/details_pdf.html"
    event = Event.objects.get(event_id=event_id)
    context = {"event": event, }
    return pdf.generateHttpResponse(request, context, template_name)


def event_list_pdf(request):
    template_name = "bportal_modules/details/events/list_pdf.html"
    query_result, _ = event_filtering(request)
    context = {"events": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def event_csv(request):
    query_result, _ = event_filtering(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="events.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)    
    for q in query_result['filter'].qs:
        writer.writerow([q.event_name_text, q.event_date_from , '-', q.event_date_to, q.event_category, [x.institution_fullname for x in q.event_institutions.all()]])
    return response

 
class EventDetailView(generic.DetailView):
    model = Event
    template_name = 'bportal_modules/details/events/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'event_name_slug'
    query_pk_and_slug = True
    
    def get_object(self, *args, **kwargs):     
        event = super(EventDetailView, self).get_object(*args, **kwargs)
        
        response_dict, event.curr_page = event_filtering(self.request)
        event.filter = response_dict['filter'] if 'filter' in response_dict else None
        event.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
        
        return check_event_read_permission(self.request.user, event)
    
    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context
    

class EventCreateView(CreateWithInlinesView, ChangeMessageView):
    model = Event
    form_class = EventForm
    inlines = [EventFileInline, EventLinkInline, EventContentContributionInline]
    template_name = 'bportal_modules/details/events/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            name = request.POST['event_name']
            name = remove_unnecessary_tags_from_title(name)
            name = strip_tags(name)            
            dup_list = Event.objects.filter(event_name_text=name)  
            if dup_list:         
                if (self.form_class is not ConfirmEventModelForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageEvent.DUPLICATE)
                else:
                    self.form_class = EventForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(EventCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmEventModelForm if self.duplicate else self.form_class
        
    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.event_added_by = user
        form.instance.event_modified_by = user
        form.instance.event_name = remove_unnecessary_tags_from_title(form.instance.event_name)
        form.instance.event_name_text = strip_tags(form.instance.event_name)
        form.instance.event_name_slug = slugify_text_title(form.instance.event_name_text)
        
        response = super(EventCreateView, self).forms_valid(form, inlines)
                
        modification = EventModification.objects.create(event=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            EventAuthorized.objects.create(event=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)        

        return response


class EventUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = Event
    form_class = EventForm
    inlines = [EventFileInline, EventLinkInline, EventContentContributionInline]
    template_name = 'bportal_modules/details/events/edit.html'
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EventUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        event = super(EventUpdateView, self).get_object(*args, **kwargs)
        return check_event_write_permission(self.request.user, event)
            
    def forms_valid(self, form, inlines):
        user = self.request.user 
        form.instance.event_modified_by = user
        form.instance.event_date_edit = timezone.now()
        form.instance.event_name = remove_unnecessary_tags_from_title(form.instance.event_name)
        form.instance.event_name_text = strip_tags(form.instance.event_name)
        form.instance.event_name_slug = slugify_text_title(form.instance.event_name_text)
        
        response = super(EventUpdateView, self).forms_valid(form, inlines)
                
        modification = EventModification.objects.create(event=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)

        return response


class EventDeleteView(generic.DeleteView):
    model = Event
    template_name = 'bportal_modules/details/events/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('event_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EventDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        event = super(EventDeleteView, self).get_object(*args, **kwargs)
        return check_event_write_permission(self.request.user, event)



class EventSummaryDetailView(generic.DetailView):
    model = EventSummary
    template_name = 'bportal_modules/details/events/summary/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'event_name_slug'
    query_pk_and_slug = True    
    
    def get_queryset(self):
        return Event.objects.all()
    
    def get_object(self, *args, **kwargs):     
        event = super(EventSummaryDetailView, self).get_object(*args, **kwargs)
        event_summary = event.event_summary
        if has_event_read_permission(self.request.user, event):
            return event_summary        
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(EventSummaryDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context        
        

class EventSummaryCreateView(CreateWithInlinesView, ChangeMessageView):
    model = EventSummary
    form_class = EventSummaryForm
    inlines = [EventSummaryLinkInline, EventSummaryFileInline, EventSummaryPictureInline, EventSummaryPublicationInline, EventSummaryContentContributionInline]
    template_name = 'bportal_modules/details/events/summary/create.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        event_id = self.request.GET.get('event_id', None)
        try:
            event = Event.objects.get(event_id=event_id)
            if has_event_write_permission(self.request.user, event):
                return super(EventSummaryCreateView, self).dispatch(*args, **kwargs)        
            else:
                raise PermissionDenied
        except Event.DoesNotExist:
            raise Http404  

    
    def get_initial(self):
        initial = super(EventSummaryCreateView, self).get_initial()
        initial = initial.copy()
        event_id = self.request.GET.get('event_id', None)
        initial['event_summary_event'] = event_id
        return initial
    
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.event_summary_added_by = user
        form.instance.event_summary_date_add = timezone.now()
        
        response = super(EventSummaryCreateView, self).forms_valid(form, inlines)
        
        self.object.event_summary_event.event_modified_by = user
        self.object.event_summary_event.event_date_edit = form.instance.event_summary_date_add
        self.object.event_summary_event.save()
        
        modification = EventModification.objects.create(event=self.object.event_summary_event, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)        
                
        return response


class EventSummaryUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = EventSummary
    form_class = EventSummaryForm
    inlines = [EventSummaryLinkInline, EventSummaryFileInline, EventSummaryPictureInline, EventSummaryPublicationInline, EventSummaryContentContributionInline]
    template_name = 'bportal_modules/details/events/summary/edit.html'
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EventSummaryUpdateView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Event.objects.all()    
    
    def get_object(self, *args, **kwargs):     
        event = super(EventSummaryUpdateView, self).get_object(*args, **kwargs)
        event_summary = event.event_summary
        if has_event_write_permission(self.request.user, event_summary.event_summary_event):
            return event_summary        
        else:
            raise PermissionDenied        
        
    def forms_valid(self, form, inlines):
        user = self.request.user
        
        response = super(EventSummaryUpdateView, self).forms_valid(form, inlines)

        self.object.event_summary_event.event_modified_by = user
        self.object.event_summary_event.event_date_edit = timezone.now()
        self.object.event_summary_event.save()
               
        modification = EventModification.objects.create(event=self.object.event_summary_event, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)
        
        return response


class EventSummaryDeleteView(generic.DeleteView):
    model = EventSummary
    template_name = 'bportal_modules/details/events/summary/delete.html'
    pk_url_kwarg = 'id'
       
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EventSummaryDeleteView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Event.objects.all() 
    
    def get_object(self, *args, **kwargs):
        event = super(EventSummaryDeleteView, self).get_object(*args, **kwargs)
        event_summary = event.event_summary
        if has_event_write_permission(self.request.user, event_summary.event_summary_event):
            self.success_url = event_summary.event_summary_event.get_absolute_url()
            return event_summary        
        else:
            raise PermissionDenied  
