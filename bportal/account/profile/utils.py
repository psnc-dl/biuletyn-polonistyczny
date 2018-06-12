# -*- coding: utf-8 -*-
from bportal.module.common.constants import DEFAULT_PER_PAGE, NUMBER_OF_PER_PAGE_OPTIONS

from .models import UserProfile


class UserConfig:
    
    @staticmethod
    def getPerPage(request, GET):
        def_per_page = UserConfig.__getDefPerPage(request)
        per_page = GET.get('per_page', None)
        if not per_page:
            per_page = def_per_page
        else:
            per_page = int(per_page)
        if per_page != def_per_page:
            UserConfig.__setDefPerPage(request, per_page)
        return per_page       
    
    @staticmethod
    def __getDefPerPage(request):
        def_per_page = DEFAULT_PER_PAGE
        user = request.user
        if user.is_authenticated():
            profile = UserProfile.objects.get(user=user)
            if profile is not None:
                def_per_page = profile.user_items_per_page
            elif request.session.get('last_per_page'):
                def_per_page = int(request.session.get('last_per_page'))
        elif request.session.get('last_per_page'):
            def_per_page = int(request.session.get('last_per_page'))
        return def_per_page
    
    @staticmethod
    def __setDefPerPage(request, per_page):
        user = request.user
        if user.is_authenticated():
            profile = UserProfile.objects.get(user=user)
            if profile is not None:
                profile.user_items_per_page = per_page
                profile.save()
            else:
                request.session['last_per_page'] = per_page        
        else:
            request.session['last_per_page'] = per_page        
                
    
    @staticmethod
    def perPageChoices():
        perPage = DEFAULT_PER_PAGE
        perPageChoices = [i * perPage for i in range(1, NUMBER_OF_PER_PAGE_OPTIONS)]
        return perPageChoices
    
