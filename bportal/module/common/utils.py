# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import re

from django.utils.encoding import force_text
from django.utils.text import get_text_list, slugify
from django.utils.translation import ugettext as _

from bportal.module.competition.fields import FieldCompetition
from bportal.module.dissertation.fields import FieldDissertation
from bportal.module.educationaloffer.fields import FieldEducationalOffer
from bportal.module.event.fields import FieldEvent
from bportal.module.joboffer.fields import FieldJobOffer
from bportal.module.project.fields import FieldProject
from bportal.module.scholarship.fields import FieldScholarship
import threading


logger = logging.getLogger(__name__)

def remove_unnecessary_tags_from_title(tagged_title):
    tagged_title = tagged_title.replace('<br />', '')
    tagged_title = tagged_title.replace('<br/>', '')
    tagged_title = tagged_title.replace('<br>', '')
    tagged_title = tagged_title.replace('&nbsp;', '')
    tagged_title = tagged_title.replace('\r', '')
    tagged_title = tagged_title.replace('\n', '')
    return tagged_title


def slugify_text_title(text_title):
    if text_title is None:
        return ''
    text_title = text_title.replace('ł', 'l')
    text_title = text_title.replace('Ł', 'L')
    text_title = slugify(text_title)[0:128]
    return text_title


class ExtendedPaginator():
    
    @staticmethod
    def construct_filter_string(filter_data):
        pagination_prefix = '?'
        for f_key, f_values in filter_data.lists():
            if f_key not in ['page', 'per_page']:
                for f_value in f_values:
                    pagination_prefix += '&' + str(f_key) + '=' + str(f_value)
        return pagination_prefix
   

class ImportHelper():
    pattern_rem_white = re.compile(r'\s+')
    
    @staticmethod
    def create_dict_key(*str_args):
        return ''.join([re.sub(ImportHelper.pattern_rem_white, '', s).lower() if s else '' for s in str_args])
    
    @staticmethod
    def create_shortname(name):
        """
        The method returns capitalized shortcut for institution name
        i. e. for 'Uniwersytet im. Kardynala Stefana Wyszynskiego w Warszawie'
        as result it gives 'UKSW w Warszawie' 
        """
        if name is None:
            return ''
        name = name.replace('im.', '')
        name_arr = name.split(' w ')
        shortname = ''.join([w.capitalize()[:1] if len(w) > 1 else w for w in name_arr[0].split()])
        if len(name_arr) > 1:
            shortname = ' w '.join((shortname, name_arr[1]))
        return shortname
    
    @staticmethod
    def try_parsing_date(text):
        for fmt in ('%d-%m-%Y %H:%M:%S', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')
    
    @staticmethod
    def create_date_isoformat(dtstr):
        try:
            return ImportHelper.try_parsing_date(dtstr)
        except Exception as e:
            logger.warn('Datetime parsing error: ' + str(e))
            return None
        
    @staticmethod
    def recognize_institution_names(institution_name):
        institution_subnames_arr = institution_name.split(';')
        university_name = None
        faculty_name = None
        institute_name = None
        if len(institution_subnames_arr) > 0:
            university_name = institution_subnames_arr[0]
        if len(institution_subnames_arr) > 1:
            faculty_name = institution_subnames_arr[1]
        if len(institution_subnames_arr) > 2:
            institute_name = institution_subnames_arr[2]
        return [university_name, faculty_name, institute_name]
    
    @staticmethod
    def untangle_institutions_names(institutions_names_str):
        institutions_triples = list()
        if institutions_names_str:
            institutions_names_arr = institutions_names_str.split('/')
            for institution_name in institutions_names_arr:
                institution_name = institution_name.strip()
                if not institution_name:
                    continue
                institutions_triple = ImportHelper.recognize_institution_names(institution_name)
                institutions_triples.append(institutions_triple)
        return institutions_triples

       
class RelatedObjectHelper():
    
    __categories_dict = {
        'competition'  : FieldCompetition.VERBOSE_NAME,
        'dissertation' : FieldDissertation.VERBOSE_NAME,
        'event' : FieldEvent.VERBOSE_NAME,
        'eduoffer' : FieldEducationalOffer.VERBOSE_NAME,
        'joboffer' : FieldJobOffer.VERBOSE_NAME,
        'project'  : FieldProject.VERBOSE_NAME,
        'scholarship' : FieldScholarship.VERBOSE_NAME
        }
    
    @staticmethod
    def get_category(obj_type):
        if obj_type is None:
            return None
        if obj_type in RelatedObjectHelper.__categories_dict:
            return RelatedObjectHelper.__categories_dict[obj_type]
        else:
            return obj_type


# Thread-safe singleton implementation
# See https://gist.github.com/werediver/4396488
class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance
    
    @classmethod
    def destroy_instance(cls):
        if cls.__singleton_instance:
            with cls.__singleton_lock:
                cls.__singleton_instance = None
        return cls.__singleton_instance
