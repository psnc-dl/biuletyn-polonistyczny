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

from .filters import ProjectFilter, ProjectFilterForm
from .forms import ProjectForm, ConfirmProjectForm, ProjectInstitutionInline, ProjectParticipantInline, ProjectFileInline, ProjectLinkInline, ProjectContentContributionInline
from .messages import MessageProject
from .models import Project, ProjectAuthorized, ProjectModification
from .permissions import check_project_write_permission, check_project_read_permission


def project_query(request):
    GET = request.GET.copy()

    project_status = GET.getlist('project_status')
    if not project_status:
        GET.setlist('project_status', [ProjectFilterForm.PROJECT_STATUS_IN_PROGRESS, ProjectFilterForm.PROJECT_STATUS_FINISHED])
        project_status = GET.getlist('project_status')

    project_only_my = GET.get('project_only_my')

    user = request.user
    filter_args = [];
    published = Q(project_is_accepted=True)
    owner = Q(project_added_by=user)
    modif = Q(project_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(project_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)

    if not (ProjectFilterForm.PROJECT_STATUS_FINISHED in project_status and ProjectFilterForm.PROJECT_STATUS_IN_PROGRESS in project_status):
        if ProjectFilterForm.PROJECT_STATUS_FINISHED in project_status:
            finished = Q(project_date_end__lt=timezone.now().date())
            filter_args.append(finished)    
        if ProjectFilterForm.PROJECT_STATUS_IN_PROGRESS in project_status:
            inprogress = Q(project_date_end__gte=timezone.now().date())
            unknown = Q(project_date_end__isnull=True)
            filter_args.append(inprogress | unknown)
            
    if project_only_my:
        only_my = Q(project_added_by=user)
        filter_args.append(only_my)

    # distinct because of many cities that give many regions and consequently duplicates in joins (moreover project_authorizations gives duplicates)
    qset = Project.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET]        


def project_filtering(request):
    query_result = project_query(request)
    qset = query_result[0]
    GET = query_result[2]
    
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-project_is_promoted,-project_date_add'
        o = GET.get('o')
        
    f = ProjectFilter(GET, queryset=qset)
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

    
def project_list(request):
    response_dict, _ = project_filtering(request)
    return render_to_response('bportal_modules/details/projects/list.html', response_dict, RequestContext(request))


def project_pdf(request):
    project_id = request.GET['project_id']
    template_name = "bportal_modules/details/projects/details_pdf.html"
    project = Project.objects.get(project_id=project_id)
    context = {"project": project, }
    return pdf.generateHttpResponse(request, context, template_name)


def project_list_pdf(request):
    template_name = "bportal_modules/details/projects/list_pdf.html"
    query_result, _ = project_filtering(request)           
    context = {"projects": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def project_csv(request):
    query_result, _ = project_filtering(request)     
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="projects.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.project_title_text, q.project_date_end, [x.discipline_fullname for x in q.project_disciplines.all()], [x.institution_fullname for x in q.project_institutions.all()]])
    return response


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'bportal_modules/details/projects/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'project_title_slug'
    query_pk_and_slug = True
    
    def get_object(self, *args, **kwargs):     
        project = super(ProjectDetailView, self).get_object(*args, **kwargs)
            
        response_dict, project.curr_page = project_filtering(self.request)
        project.filter = response_dict['filter'] if 'filter' in response_dict else None
        project.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
                
        return check_project_read_permission(self.request.user, project)
    
    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context


class ProjectCreateView(CreateWithInlinesView, ChangeMessageView):
    model = Project
    form_class = ProjectForm
    inlines = [ProjectParticipantInline, ProjectInstitutionInline, ProjectFileInline, ProjectLinkInline, ProjectContentContributionInline]
    template_name = 'bportal_modules/details/projects/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            title = request.POST['project_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = Project.objects.filter(project_title_text=title)  
            if dup_list:         
                if (self.form_class is not ConfirmProjectForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageProject.DUPLICATE)
                else:
                    self.form_class = ProjectForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(ProjectCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmProjectForm if self.duplicate else self.form_class

    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.project_added_by = user
        form.instance.project_modified_by = user
        form.instance.project_title = remove_unnecessary_tags_from_title(form.instance.project_title)
        form.instance.project_title_text = strip_tags(form.instance.project_title)        
        form.instance.project_title_slug = slugify_text_title(form.instance.project_title_text)

        response = super(ProjectCreateView, self).forms_valid(form, inlines)
        
        modification = ProjectModification.objects.create(project=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            ProjectAuthorized.objects.create(project=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message) 
        
        return response
    

class ProjectUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = Project
    form_class = ProjectForm
    inlines = [ProjectParticipantInline, ProjectInstitutionInline, ProjectFileInline, ProjectLinkInline, ProjectContentContributionInline]
    template_name = 'bportal_modules/details/projects/edit.html'
    pk_url_kwarg = 'id'    
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        project = super(ProjectUpdateView, self).get_object(*args, **kwargs)
        return check_project_write_permission(self.request.user, project)
    
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.project_modified_by = user
        form.instance.project_date_edit = timezone.now()
        form.instance.project_title = remove_unnecessary_tags_from_title(form.instance.project_title)
        form.instance.project_title_text = strip_tags(form.instance.project_title)       
        form.instance.project_title_slug = slugify_text_title(form.instance.project_title_text)        

        response = super(ProjectUpdateView, self).forms_valid(form, inlines)

        modification = ProjectModification.objects.create(project=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message) 
        
        return response
   

class ProjectDeleteView(generic.DeleteView):
    model = Project
    template_name = 'bportal_modules/details/projects/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('project_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        project = super(ProjectDeleteView, self).get_object(*args, **kwargs)
        return check_project_write_permission(self.request.user, project)
