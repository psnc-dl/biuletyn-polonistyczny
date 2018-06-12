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

from .filters import CompetitionFilter, CompetitionFilterForm
from .forms import CompetitionForm, ConfirmCompetitionForm, CompetitionFileInline, CompetitionLinkInline, CompetitionContentContributionInline
from .messages import MessageCompetition
from .models import Competition, CompetitionAuthorized, CompetitionModification
from .permissions import check_competition_write_permission, check_competition_read_permission


def competition_query(request):
    GET = request.GET.copy()

    competition_status = GET.getlist('competition_status')
    if not competition_status:
        GET.setlist('competition_status', [CompetitionFilterForm.COMPETITION_STATUS_IN_PROGRESS, CompetitionFilterForm.COMPETITION_STATUS_FINISHED])
        competition_status = GET.getlist('competition_status')

    competition_only_my = GET.get('competition_only_my')
    
    user = request.user
    filter_args = [];
    published = Q(competition_is_accepted=True)
    owner = Q(competition_added_by=user)
    modif = Q(competition_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(competition_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)

    if not (CompetitionFilterForm.COMPETITION_STATUS_FINISHED in competition_status and CompetitionFilterForm.COMPETITION_STATUS_IN_PROGRESS in competition_status):
        if CompetitionFilterForm.COMPETITION_STATUS_FINISHED in competition_status:
            finished = Q(competition_deadline_date__lt=timezone.now().date())
            filter_args.append(finished)    
        if CompetitionFilterForm.COMPETITION_STATUS_IN_PROGRESS in competition_status:
            inprogress = Q(competition_deadline_date__gte=timezone.now().date())
            unknown = Q(competition_deadline_date__isnull=True)
            filter_args.append(inprogress | unknown) 

    if competition_only_my:
        only_my = Q(competition_added_by=user)
        filter_args.append(only_my)

    # distinct because of many competition_authorizations that give duplicates in joins 
    qset = Competition.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET] 


def competition_filtering(request):
    query_result = competition_query(request)
    qset = query_result[0]
    GET = query_result[2]  
    
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-competition_is_promoted,-competition_date_add'
        o = GET.get('o')  
        
    f = CompetitionFilter(GET, queryset=qset)
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


def competition_list(request):
    response_dict, _ = competition_filtering(request)                
    return render_to_response('bportal_modules/details/competitions/list.html', response_dict, RequestContext(request))

     
def competition_pdf(request):
    competition_id = request.GET['competition_id']
    template_name = "bportal_modules/details/competitions/details_pdf.html"
    competition = Competition.objects.get(competition_id=competition_id)
    context = {"competition": competition, }
    return pdf.generateHttpResponse(request, context, template_name)


def competition_list_pdf(request):
    template_name = "bportal_modules/details/competitions/list_pdf.html"
    query_result, _ = competition_filtering(request)
    context = {"competitions": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def competition_csv(request):
    query_result, _ = competition_filtering(request)    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="competitions.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.competition_title_text, q.competition_deadline_date, [x.target_name for x in q.competition_targets.all()], [x.institution_fullname for x in q.competition_institutions.all()]])
    return response 

     
class CompetitionDetailView(DetailView):
    model = Competition
    template_name = 'bportal_modules/details/competitions/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'competition_title_slug'
    query_pk_and_slug = True       
        
    def get_object(self, *args, **kwargs):     
        competition = super(CompetitionDetailView, self).get_object(*args, **kwargs)
               
        response_dict, competition.curr_page = competition_filtering(self.request)
        competition.filter = response_dict['filter'] if 'filter' in response_dict else None
        competition.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
        
        return check_competition_read_permission(self.request.user, competition)
    
    def get_context_data(self, **kwargs):
        context = super(CompetitionDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context

class CompetitionCreateView(CreateWithInlinesView, ChangeMessageView):
    model = Competition
    form_class = CompetitionForm
    inlines = [CompetitionFileInline, CompetitionLinkInline, CompetitionContentContributionInline]
    template_name = 'bportal_modules/details/competitions/create.html'
    duplicate = False
        
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            title = request.POST['competition_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = Competition.objects.filter(competition_title_text=title)  
            if dup_list:         
                if (self.form_class is not ConfirmCompetitionForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageCompetition.DUPLICATE)
                else:
                    self.form_class = CompetitionForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(CompetitionCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmCompetitionForm if self.duplicate else self.form_class
    
    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.competition_added_by = user
        form.instance.competition_modified_by = user
        form.instance.competition_title = remove_unnecessary_tags_from_title(form.instance.competition_title)
        form.instance.competition_title_text = strip_tags(form.instance.competition_title)
        form.instance.competition_title_slug = slugify_text_title(form.instance.competition_title_text)         

        response = super(CompetitionCreateView, self).forms_valid(form, inlines)

        modification = CompetitionModification.objects.create(competition=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            CompetitionAuthorized.objects.create(competition=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()

        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message) 

        return response


class CompetitionUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = Competition
    form_class = CompetitionForm
    inlines = [CompetitionFileInline, CompetitionLinkInline, CompetitionContentContributionInline]
    template_name = 'bportal_modules/details/competitions/edit.html'
    pk_url_kwarg = 'id'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CompetitionUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        competition = super(CompetitionUpdateView, self).get_object(*args, **kwargs)
        return check_competition_write_permission(self.request.user, competition)
     
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.competition_modified_by = user
        form.instance.competition_date_edit = timezone.now()
        form.instance.competition_title = remove_unnecessary_tags_from_title(form.instance.competition_title)
        form.instance.competition_title_text = strip_tags(form.instance.competition_title)
        form.instance.competition_title_slug = slugify_text_title(form.instance.competition_title_text)         

        response = super(CompetitionUpdateView, self).forms_valid(form, inlines)
        
        modification = CompetitionModification.objects.create(competition=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)
        
        return response
 
 
class CompetitionDeleteView(generic.DeleteView):
    model = Competition
    template_name = 'bportal_modules/details/competitions/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('competition_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CompetitionDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        competition = super(CompetitionDeleteView, self).get_object(*args, **kwargs)
        return check_competition_write_permission(self.request.user, competition)
    
