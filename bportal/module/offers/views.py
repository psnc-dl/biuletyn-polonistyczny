# -*- coding: utf-8 -*-
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from bportal.account.profile.models import UserProfile
from bportal.module.educationaloffer.models import EducationalOffer
from bportal.module.joboffer.models import JobOffer
from bportal.module.scholarship.models import Scholarship


def offers_list(request):
    user = request.user
    
    #joboffers
    joboffers_filter_args = [];
    published = Q(joboffer_is_accepted=True)
    owner = Q(joboffer_added_by=user)
    modif = Q(joboffer_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(joboffer_authorizations__in=profile.user_institution.all())
            joboffers_filter_args.append(published | owner | modif | inst)
    else:
        joboffers_filter_args.append(published)    
    promoted_joboffers = JobOffer.objects.filter(joboffer_is_promoted=True, *joboffers_filter_args).order_by('-joboffer_date_add')
    newest_joboffers = JobOffer.objects.filter(joboffer_is_promoted=False, *joboffers_filter_args).order_by('-joboffer_date_add')[:10]
    
    #eduoffers
    eduoffers_filter_args = [];
    published = Q(eduoffer_is_accepted=True)
    owner = Q(eduoffer_added_by=user)
    modif = Q(eduoffer_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(eduoffer_authorizations__in=profile.user_institution.all())
            eduoffers_filter_args.append(published | owner | modif | inst)
    else:
        eduoffers_filter_args.append(published)    
    promoted_eduoffers = EducationalOffer.objects.filter(eduoffer_is_promoted=True, *eduoffers_filter_args).order_by('-eduoffer_date_add')
    newest_eduoffers = EducationalOffer.objects.filter(eduoffer_is_promoted=False, *eduoffers_filter_args).order_by('-eduoffer_date_add')[:10]
    
    #scholarships
    scholarships_filter_args = [];
    published = Q(scholarship_is_accepted=True)
    owner = Q(scholarship_added_by=user)
    modif = Q(scholarship_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(scholarship_authorizations__in=profile.user_institution.all())
            scholarships_filter_args.append(published | owner | modif | inst)
    else:
        scholarships_filter_args.append(published)    
    promoted_scholarships = Scholarship.objects.filter(scholarship_is_promoted=True, *scholarships_filter_args).order_by('-scholarship_date_add')
    newest_scholarships = Scholarship.objects.filter(scholarship_is_promoted=False, *scholarships_filter_args).order_by('-scholarship_date_add')[:10]
    
    response_dict = dict()
    response_dict['promoted_joboffers'] = promoted_joboffers
    response_dict['newest_joboffers'] = newest_joboffers
    response_dict['promoted_eduoffers'] = promoted_eduoffers
    response_dict['newest_eduoffers'] = newest_eduoffers
    response_dict['promoted_scholarships'] = promoted_scholarships
    response_dict['newest_scholarships'] = newest_scholarships
    
    return render_to_response('bportal_modules/details/offers/list.html', response_dict, RequestContext(request))