# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django_addanother.views import CreatePopupMixin
from extra_views.advanced import CreateWithInlinesView
import reversion

from bportal.module.common.permissions import has_create_permission
from bportal.module.common.utils import slugify_text_title
from bportal.module.common.view import ChangeMessageView

from .forms import PersonForm, ConfirmPersonForm, PersonAffiliationInline
from .messages import MessagePerson
from .models import Person 


class PersonDetailView(DetailView):
    model = Person
    template_name = 'bportal_modules/details/people/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'person_slug'
    query_pk_and_slug = True    

    
class PersonCreateView(CreatePopupMixin, CreateWithInlinesView, ChangeMessageView):
    model = Person
    form_class = PersonForm
    inlines = [PersonAffiliationInline]
    template_name = 'bportal_modules/details/people/create.html'
    duplicate = False   
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            first_name = request.POST['person_first_name']
            last_name = request.POST['person_last_name']
            dup_list = Person.objects.filter(person_first_name=first_name, person_last_name=last_name)  
            if dup_list:         
                if (self.form_class is not ConfirmPersonForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessagePerson.DUPLICATE)
                else:
                    self.form_class = PersonForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(PersonCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ConfirmPersonForm if self.duplicate else self.form_class
    
    def forms_valid(self, form, inlines):    
        if self.duplicate:
            return self.forms_invalid(form, inlines)        
        if self.is_popup():
            self.success_url = '/'
            
        form.instance.person_slug = slugify_text_title(form.instance.person_first_name + ' ' + form.instance.person_last_name)   
        response = super(PersonCreateView, self).forms_valid(form, inlines)
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)
                
        if self.is_popup():
            return self.respond_script(self.object)
        else:
            return response

