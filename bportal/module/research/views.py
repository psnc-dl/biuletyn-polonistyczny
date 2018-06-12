# -*- coding: utf-8 -*-
from django.db.models import Q
from django.template.context import RequestContext
from bportal.module.project.models import Project
from django.shortcuts import render_to_response
from bportal.module.dissertation.models import Dissertation
from bportal.module.competition.models import Competition
from bportal.account.profile.models import UserProfile

def research_list(request):
    user = request.user
    
    #projects
    projects_filter_args = [];
    published = Q(project_is_accepted=True)
    owner = Q(project_added_by=user)
    modif = Q(project_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(project_authorizations__in=profile.user_institution.all())
            projects_filter_args.append(published | owner | modif | inst)
    else:
        projects_filter_args.append(published)    
    promoted_projects = Project.objects.filter(project_is_promoted=True, *projects_filter_args).order_by('-project_date_add')
    newest_projects = Project.objects.filter(project_is_promoted=False, *projects_filter_args).order_by('-project_date_add')[:10]
    
    #dissertations
    dissertations_filter_args = [];
    published = Q(dissertation_is_accepted=True)
    owner = Q(dissertation_added_by=user)
    modif = Q(dissertation_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(dissertation_authorizations__in=profile.user_institution.all())
            dissertations_filter_args.append(published | owner | modif | inst)
    else:
        dissertations_filter_args.append(published)    
    promoted_dissertations = Dissertation.objects.filter(dissertation_is_promoted=True, *dissertations_filter_args).order_by('-dissertation_date_add')
    newest_dissertations = Dissertation.objects.filter(dissertation_is_promoted=False, *dissertations_filter_args).order_by('-dissertation_date_add')[:10]
    
    #competitions
    competitions_filter_args = [];
    published = Q(competition_is_accepted=True)
    owner = Q(competition_added_by=user)
    modif = Q(competition_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(competition_authorizations__in=profile.user_institution.all())
            competitions_filter_args.append(published | owner | modif | inst)
    else:
        competitions_filter_args.append(published)    
    promoted_competitions = Competition.objects.filter(competition_is_promoted=True, *competitions_filter_args).order_by('-competition_date_add')
    newest_competitions = Competition.objects.filter(competition_is_promoted=False, *competitions_filter_args).order_by('-competition_date_add')[:10]
    
    response_dict = dict()
    response_dict['promoted_projects'] = promoted_projects
    response_dict['newest_projects'] = newest_projects
    response_dict['promoted_dissertations'] = promoted_dissertations
    response_dict['newest_dissertations'] = newest_dissertations
    response_dict['promoted_competitions'] = promoted_competitions
    response_dict['newest_competitions'] = newest_competitions
    
    return render_to_response('bportal_modules/details/research/list.html', response_dict, RequestContext(request))