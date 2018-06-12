# -*- coding: utf-8 -*-
import datetime
import logging

from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator
from import_export import fields, resources
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget

from bportal.module.common.utils import slugify_text_title, ImportHelper, SingletonMixin
from bportal.module.institution.models import Institution
from bportal.module.person.models import ScientificTitle, Person

from .models import Dissertation, DissertationAuthorized


# Get an instance of a logger
logger = logging.getLogger(__name__)
import_report = logging.getLogger('dissertations_import_report')

class DissertationImportHelper(SingletonMixin):
    
    LOG_MSG_SUCC_DATABASE_CREATE_INST = "[CREATE] Create new institution object in database: "
    LOG_MSG_SUCC_DATABASE_GET_INST = "[UPDATE] Get institution object from database: "
    
    LOG_MSG_ERR_DATABASE_CREATE_INST = "[ERROR] Problem with create new institution object in database: "
    LOG_MSG_ERR_DATABASE_GET_INST = "[ERROR] On get institution object from database: "
    
    LOG_MSG_SUCC_DATABASE_GET_DISS = "[UPDATE] Get dissertation object from database: "
    LOG_MSG_ERR_DATABASE_GET_DISS = "[ERROR] On get dissertation object from database: "
    
    REPORT_INSTITUTION_CREATED = 'Dodano instytucję'
    REPORT_INSTITUTION_UPDATED = 'Zaktualizowano instytucję'
    REPORT_INSTITUTION_CANNOT_CREATE = 'Nie można utworzyć instytucji'
    REPORT_INSTITUTION_NOT_FOUND = 'Nie znaleziono instytucji'
    REPORT_DISSERTATION_NOT_FOUND = 'Nie znaleziono pracy'
    
    def __init__(self):
        # scientific titles
        self.MARK_PROF = 'prof'
        self.MARK_DR = 'dr'
        self.MARK_MGR = 'prof'
        scientific_titles = list(ScientificTitle.objects.all());
        self._prof_t = [t for t in scientific_titles if self.MARK_PROF in t.scientific_title_abbreviation][0]
        self._dr_t = [t for t in scientific_titles if self.MARK_DR in t.scientific_title_abbreviation][0]
        self._mgr_t = [t for t in scientific_titles if self.MARK_MGR in t.scientific_title_abbreviation][0]
        
        institutions = Institution.objects.all();
        self.institutions_dict = dict((ImportHelper.create_dict_key(i.get_as_dict_key), i) for i in institutions)
        
        # people dictionary and set of ids
        people = list(Person.objects.all());
        self.people_ids = set(d.person_id for d in people)
        self.people_dict = dict((ImportHelper.create_dict_key(p.person_first_name, p.person_last_name), p.person_id) for p in people)
        self.dict_opi_id_person_id = dict((p.person_opi_id, p.person_id) for p in people)
        self.max_person_id = max(self.people_ids)
        
        # role
        self.MARK_AUTHOR = 'autor'
        self.MARK_REVIEWER = 'recenz'
        self.MARK_SUPERVISOR = 'promot'
        
        # dissertations dictionary
        dissertations = list(Dissertation.objects.all().prefetch_related("dissertation_institution", "dissertation_supervisors", "dissertation_reviewers", "dissertation_author"));
        self.dissertations_ids_dict = dict((d.dissertation_id, d) for d in dissertations)
        self.dissertations_ids = set(d.dissertation_id for d in dissertations)
        self.dissertations_opi_ids = set(d.dissertation_opi_id for d in dissertations)
        self.dict_opi_id_dissertation_id = dict((d.dissertation_opi_id, d.dissertation_id) for d in dissertations)
        self.max_dissertation_id = max(self.dissertations_ids) if len(self.dissertations_ids) > 0 else 0
        self.dissertations_dict = dict((ImportHelper.create_dict_key(d.dissertation_title_text), d.dissertation_id) for d in dissertations)
        
    def get_scientific_title(self, deg):
        scientific_title = None
        if self.MARK_PROF in deg:
            scientific_title = self._prof_t
        elif self.MARK_DR in deg:
            scientific_title = self._dr_t
        elif self.MARK_MGR in deg:
            scientific_title = self._mgr_t
            
        return scientific_title
    

    def get_or_create_institution_object(self, institution_name, parent=None):
        institution = None
        dict_key = institution_name
        if parent is not None:
            dict_key = dict_key + parent.institution_shortname
        institution_key = ImportHelper.create_dict_key(dict_key)
        if (institution_key not in self.institutions_dict):
            
            # truncator add tree dots at the end and do smth else
            inst_shortname = Truncator(ImportHelper.create_shortname(institution_name)).chars(32)
            inst_slug = slugify_text_title(inst_shortname)
            if parent:
                institution = Institution.objects.create(institution_shortname=inst_shortname, institution_fullname=institution_name, institution_slug=inst_slug, institution_parent=parent)
            else:
                institution = Institution.objects.create(institution_shortname=inst_shortname, institution_fullname=institution_name, institution_slug=inst_slug)
            self.institutions_dict[institution_key] = institution
            logger.info(self.LOG_MSG_SUCC_DATABASE_CREATE_INST + 'get_or_create_institution_object institution_name=' + institution_name + ' institution_id=' + str(institution.institution_id))
            import_report.info(';'.join((self.REPORT_INSTITUTION_CREATED, str(institution.institution_id), '', '', '', institution_name)))
        else:
            institution = self.institutions_dict[institution_key]
        return institution
    
    def get_institutions(self, institutions_names_str):
        institutions_triples = ImportHelper.untangle_institutions_names(institutions_names_str)
        institutions = list()
        for [university_name, faculty_name, _] in institutions_triples:
            if university_name:
                university = self.get_or_create_institution_object(university_name)
                if faculty_name:
                    faculty = self.get_or_create_institution_object(faculty_name, university)
                    institutions.append(faculty)
                else:
                    institutions.append(university)
        return institutions
       
    def get_person_id(self, row_person_opi_id):
        [opi_id_exist, proposed_id] = self.check_person_opi_id(row_person_opi_id)
        if opi_id_exist:
            return proposed_id
         
# #iNOTE: the code below may be used when we would like to create person form people functions file
#         proposed_id = self.max_person_id + 1
#         while ((proposed_id in self.people_ids) and (proposed_id > 0)):
#             self.max_person_id += 1
#             proposed_id = self.max_person_id
#         self.people_ids.add(proposed_id)
        
        return proposed_id
    
    def get_dissertation_id(self, row_dissertation_opi_id):
        [opi_id_exist, proposed_id] = self.check_dissertation_opi_id(row_dissertation_opi_id)
        
        return [opi_id_exist, proposed_id]
    
    def get_dissertation_type(self, row_dissertation_type):
        if row_dissertation_type is None:
            return None
        if  'hab' in row_dissertation_type:
            return Dissertation.DISSERTATION_TYPE_HAB
        else: 
            return Dissertation.DISSERTATION_TYPE_DOC
        
    def check_dissertation_opi_id(self, proposed_opi_id):
        proposed_opi_id = int(proposed_opi_id)
        opi_id_exist = proposed_opi_id in self.dissertations_opi_ids
        dissertation_id = self.dict_opi_id_dissertation_id.get(proposed_opi_id, None)
        return [opi_id_exist, dissertation_id]
    
    def check_dissertation_title(self, dtitle):
        dissertation_key = ImportHelper.create_dict_key(dtitle)
        dissertation_id = None
        dissertation_key_exist = dissertation_key in self.dissertations_dict
        if dissertation_key_exist:
            dissertation_id = self.dissertations_dict[dissertation_key]
        return [dissertation_key_exist, dissertation_id]
    
    def check_person_opi_id(self, proposed_opi_id):
        if not proposed_opi_id:
            return [False, None]
        
        proposed_opi_id = int(proposed_opi_id) if proposed_opi_id else '0'
        opi_id_exist = proposed_opi_id in self.dict_opi_id_person_id
        person_id = self.dict_opi_id_person_id.get(proposed_opi_id, None)
        return [opi_id_exist, person_id]
    
    def is_supervisor(self, row_person_function):
        if row_person_function is None:
            return False
        if self.MARK_SUPERVISOR in row_person_function:
            return True
        else:
            return False
    
    def is_reviewer(self, row_person_function):
        if row_person_function is None:
            return False
        if self.MARK_REVIEWER in row_person_function:
            return True
        else:
            return False
        
    def is_author(self, row_person_function):
        if row_person_function is None:
            return False
        if self.MARK_AUTHOR in row_person_function:
            return True
        else:
            return False
    
    def get_dissertation_object(self, dissertation_id):
        dissertation = None
        if dissertation_id in self.dissertations_ids_dict:
            try:
                dissertation = self.dissertations_ids_dict[dissertation_id]
                logger.info(self.LOG_MSG_SUCC_DATABASE_GET_DISS + ' get_dissertation_object ' + ' dissertation_id=' + str(dissertation_id))
            except Exception:
                logger.error(self.LOG_MSG_ERR_DATABASE_GET_DISS + ' get_dissertation_object ' + ' dissertation_id=' + str(dissertation_id))
                import_report.error(';'.join((self.REPORT_DISSERTATION_NOT_FOUND, str(dissertation_id))))
        return dissertation
    
    def get_reviewers(self, dissertation):
        if dissertation is None:
            return []
        reviewers = [ r.person_id for r in dissertation.dissertation_reviewers.all()]
        return reviewers
    
    def get_supervisors(self, dissertation):
        if dissertation is None:
            return []
        supervisors = [ r.person_id for r in dissertation.dissertation_supervisors.all()]
        return supervisors
    
    
    def try_get_dissertation_object(self, row_dissertation_opi_id):
        [opi_id_exists, dissertation_id] = self.get_dissertation_id(row_dissertation_opi_id)
        dissertation = None
        if opi_id_exists:
            dissertation = self.get_dissertation_object(dissertation_id)
        return [dissertation, dissertation_id]
    
class DissertationResource(resources.ModelResource):
    COLUMN_DISSERTATION_ID = 'TMP_DISSERTATION_ID'
    COLUMN_DISSERTATION_OPI_ID = 'PRACE_BADAWCZE_ID'
    COLUMN_DISSERTATION_TITLE = 'TYTUL'
    COLUMN_DISSERTATION_TITLE_SLUG = 'TMP_TITLE_SLUG'
    COLUMN_DISSERTATION_TITLE_TEXT = 'TMP_TITLE_TEXT'
    COLUMN_DISSERTATION_TYPE = 'RODZAJ_PRACY'
    COLUMN_DISSERTATION_SUPERVISORS = 'TMP_DISSERTATION_SUPERVISORS'
    COLUMN_DISSERTATION_REVIEWERS = 'TMP_DISSERTATION_REVIEWERS'
    COLUMN_DISSERTATION_AUTHOR = 'TMP_DISSERTATION_AUTHOR'
    COLUMN_DISSERTATION_DATE_START = 'DATA_ROZPOCZECIA'
    COLUMN_DISSERTATION_DATE_END = 'DATA_ZAKONCZENIA'
    COLUMN_DISSERTATION_INSTITUTION = 'NAZWA_INST'
    COLUMN_DISSERTATION_IS_ACCEPTED = 'TMP_DISSERTATION_IS_ACCEPTED';
    
    # columns for people-disstertations associations
    COLUMN_PERSON_FUNCTION = 'FUNKCJA_OSOBY'
    COLUMN_PERSON_OPI_ID = 'OSOBY_ID'
    COLUMN_PERSON_FIRST_NAME = 'IMIE'
    COLUMN_PERSON_LAST_NAME = 'NAZWISKO'
    COLUMN_PERSON_DEGREE = 'STOPIEN'
    
    dissertation_id = fields.Field(column_name=COLUMN_DISSERTATION_ID, attribute='dissertation_id')
    dissertation_opi_id = fields.Field(column_name=COLUMN_DISSERTATION_OPI_ID, attribute='dissertation_opi_id')
    dissertation_title = fields.Field(column_name=COLUMN_DISSERTATION_TITLE, attribute='dissertation_title')
    dissertation_title_text = fields.Field(column_name=COLUMN_DISSERTATION_TITLE_TEXT, attribute='dissertation_title_text')
    dissertation_title_slug = fields.Field(column_name=COLUMN_DISSERTATION_TITLE_SLUG, attribute='dissertation_title_slug')
    dissertation_date_start = fields.Field(column_name=COLUMN_DISSERTATION_DATE_START, attribute='dissertation_date_start')
    dissertation_date_end = fields.Field(column_name=COLUMN_DISSERTATION_DATE_END, attribute='dissertation_date_end')
    dissertation_author = fields.Field(column_name=COLUMN_DISSERTATION_AUTHOR, attribute='dissertation_author', widget=ForeignKeyWidget(Person, field='person_id'))
    dissertation_supervisors = fields.Field(column_name=COLUMN_DISSERTATION_SUPERVISORS, attribute='dissertation_supervisors', widget=ManyToManyWidget(Person, separator=',', field='person_id'))
    dissertation_reviewers = fields.Field(column_name=COLUMN_DISSERTATION_REVIEWERS, attribute='dissertation_reviewers', widget=ManyToManyWidget(Person, separator=',', field='person_id'))
    dissertation_institution = fields.Field(column_name=COLUMN_DISSERTATION_INSTITUTION, attribute='dissertation_institution', widget=ForeignKeyWidget(Institution, field='institution_id'))
    dissertation_type = fields.Field(column_name=COLUMN_DISSERTATION_TYPE, attribute='dissertation_type')
    dissertation_is_accepted = fields.Field(column_name=COLUMN_DISSERTATION_IS_ACCEPTED, attribute='dissertation_is_accepted')
    
    LOG_MSG_ERR_FILE_IMPROPER = "[ERROR] Not proper input file for import Dissertation objects. Please check if following columns exist: "
    LOG_MSG_ADDED_OBJECT = "[SUCCESS] Dissertation object has been successfully saved. "
    LOG_MSG_DUPLICATE_OBJECT = "[DUPLICATE] Dissertation object potentially duplicated: "
    LOG_MSG_IMPORT_BEGIN = "[STARTED IMPORT] --- IMPORT DISSERTATIONS PROCESS INITIALIZED --- "
    LOG_MSG_IMPORT_END = "[FINISHED IMPORT] --- IMPORT DISSERTATIONS PROCESS FINISHED --- "
    LOG_MSG_ADDED_OBJECT = "[SUCCESS] Dissertation object has been successfully saved. "
    LOG_MSG_ERROR_MISSIG_DISSERTATION = "[NOT FOUND OBJECT] Dissertation object not found in database! "
    LOG_MSG_ERROR_MISSIG_PERSON = "[NOT FOUND OBJECT] Person object not found in database! "
    
    REPORT_FILE_IMPROPER = 'Nie poprawny format pliku dla importu prac doktorskich i habilitacyjnych. Sprawdź czy plik zawiera następujące kolumny:'
    REPORT_IMPORT_BEGIN = '--- -- - POCZĄTEK IMPORTU - -- ---'
    REPORT_IMPORT_END = '--- -- - KONIEC IMPORTU - -- ---'
    REPORT_DISSERTATION_NEW = 'Nowa praca'
    REPORT_DISSERTATION_NEW_EXIST_DUPLICATES = 'Nowa praca. Istnieją potencjalne duplikaty'
    REPORT_DISSERTATION_SAVED = 'Zapisano pracę'
    REPORT_DISSERTATION_UPDATE = 'Aktualizacja pracy. Znaleziono pracę o takim samym ID.'
    REPORT_DISSERTATION_DUPLICATE = 'Potencjalny duplikat pracy'
    REPORT_DISSERTATION_AUTHOR = 'Dodano autora pracy'
    REPORT_DISSERTATION_SUPERVISOR = 'Dodano promotora pracy'
    REPORT_DISSERTATION_REVIEWER = 'Dodano recenzenta'
    REPORT_SKIP_ROW = 'Pominięto wiersz'
    
    def __init__(self):
        self._row_to_skip = False
        self._skip_msg = '[SKIPPED ROW] '
        self._resource_info = ''
        self.ENTITY_IS_ACCEPTED = False
    
    def create_resource_info(self, row):
        return '[SKIPPED ROW] [' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] ' + '; '.join('{}={}'.format(k, v) for k, v in row.items())
    
    def get_skip_msg(self):
        return self._skip_msg
    
    def mark_row_to_skip(self, row=dict(), reason_msg=''):
        self._row_to_skip = True
        self._skip_msg = reason_msg + self.create_resource_info(row)
        
    def init_dissertation_row(self, row, is_dissertations_file):
        row_dissertation_opi_id = row.get(self.COLUMN_DISSERTATION_OPI_ID, '')
        [dissertation, dissertation_id] = self.dissertation_import_helper.try_get_dissertation_object(row_dissertation_opi_id)
        row[self.COLUMN_DISSERTATION_ID] = dissertation_id
        
        if dissertation is None:
            if (is_dissertations_file):
                row[self.COLUMN_DISSERTATION_AUTHOR] = None
                row[self.COLUMN_DISSERTATION_REVIEWERS] = None
                row[self.COLUMN_DISSERTATION_SUPERVISORS] = None
                row[self.COLUMN_DISSERTATION_IS_ACCEPTED] = self.ENTITY_IS_ACCEPTED
            else:
                #row[self.COLUMN_DISSERTATION_OPI_ID] = None
                row[self.COLUMN_DISSERTATION_AUTHOR] = None
                row[self.COLUMN_DISSERTATION_INSTITUTION] = None
                row[self.COLUMN_DISSERTATION_TITLE] = row[self.COLUMN_PERSON_FIRST_NAME] + ' ' + row[self.COLUMN_PERSON_LAST_NAME]
                row[self.COLUMN_DISSERTATION_TITLE_TEXT] = None
                row[self.COLUMN_DISSERTATION_TITLE_SLUG] = None
                row[self.COLUMN_DISSERTATION_DATE_START] = None
                row[self.COLUMN_DISSERTATION_DATE_END] = None
                row[self.COLUMN_DISSERTATION_TYPE] = None
                self.mark_row_to_skip(row, self.LOG_MSG_ERROR_MISSIG_DISSERTATION)  # #NOTE: there is no information about dissertation in dissertations-people file
        else:
            if (is_dissertations_file):
                # row[self.COLUMN_DISSERTATION_AUTHOR] = dissertation.dissertation_author
                row[self.COLUMN_DISSERTATION_REVIEWERS] = ','.join([str(r.person_id) for r in dissertation.dissertation_reviewers.all()])
                row[self.COLUMN_DISSERTATION_SUPERVISORS] = ','.join([str(s.person_id) for s in dissertation.dissertation_supervisors.all()])
                row[self.COLUMN_DISSERTATION_IS_ACCEPTED] = dissertation.dissertation_is_accepted
            else:
                row[self.COLUMN_DISSERTATION_OPI_ID] = dissertation.dissertation_opi_id
                row[self.COLUMN_DISSERTATION_INSTITUTION] = dissertation.dissertation_institution.institution_id
                row[self.COLUMN_DISSERTATION_TITLE] = dissertation.dissertation_title
                row[self.COLUMN_DISSERTATION_TITLE_TEXT] = dissertation.dissertation_title_text
                row[self.COLUMN_DISSERTATION_TITLE_SLUG] = dissertation.dissertation_title_slug
                row[self.COLUMN_DISSERTATION_DATE_START] = dissertation.dissertation_date_start
                row[self.COLUMN_DISSERTATION_DATE_END] = dissertation.dissertation_date_end
                row[self.COLUMN_DISSERTATION_TYPE] = dissertation.dissertation_type
            
        return [row, dissertation]
    
    def get_people_and_functions(self, row, dissertation):
            
        # get person_id using opi_id
        row_person_opi_id = row.get(self.COLUMN_PERSON_OPI_ID, '')
        person_id = self.dissertation_import_helper.get_person_id(row_person_opi_id)
        reviewers = self.dissertation_import_helper.get_reviewers(dissertation)
        supervisors = self.dissertation_import_helper.get_supervisors(dissertation)
            
        if person_id is None:
            self.mark_row_to_skip(row, self.LOG_MSG_ERROR_MISSIG_PERSON)  # #NOTE: there is no information about person in dissertations-people file
            
        row_dissertation_person_function = row.get(self.COLUMN_PERSON_FUNCTION, '')
        if row_dissertation_person_function is not None:
            if self.dissertation_import_helper.is_author(row_dissertation_person_function):
                row[self.COLUMN_DISSERTATION_AUTHOR] = person_id
            if self.dissertation_import_helper.is_reviewer(row_dissertation_person_function):
                if person_id not in reviewers:
                    reviewers.append(person_id)
                    row[self.COLUMN_DISSERTATION_REVIEWERS] = ','.join(str(r) for r in reviewers)
                    import_report.info(';'.join((self.REPORT_DISSERTATION_REVIEWER, str(person_id), '', str(row_person_opi_id))))                        
            if self.dissertation_import_helper.is_supervisor(row_dissertation_person_function):
                if person_id not in supervisors:
                    supervisors.append(person_id)
                    row[self.COLUMN_DISSERTATION_REVIEWERS] = ','.join(str(r) for r in reviewers)
                    import_report.info(';'.join((self.REPORT_DISSERTATION_SUPERVISOR, str(person_id), '', str(row_person_opi_id))))
                row[self.COLUMN_DISSERTATION_SUPERVISORS] = ','.join(str(s) for s in supervisors)
        
        return row
    
    def get_dissertation_data(self, row):
        # get dissertation_institutions
        row_dissertation_institutions = row.get(self.COLUMN_DISSERTATION_INSTITUTION, '')
        if not isinstance(row_dissertation_institutions, int):
            institutions = self.dissertation_import_helper.get_institutions(row_dissertation_institutions)
            row[self.COLUMN_DISSERTATION_INSTITUTION] = institutions[0].institution_id if institutions is not None and len(institutions) > 0 else None                      
        
        # get dissertation_title ant title_slug
        row_dissertation_opi_id = row.get(self.COLUMN_DISSERTATION_OPI_ID, '')
        row_dissertation_title = row.get(self.COLUMN_DISSERTATION_TITLE, '')
        text_title = strip_tags(row_dissertation_title)
        row[self.COLUMN_DISSERTATION_TITLE_TEXT] = text_title
        row[self.COLUMN_DISSERTATION_TITLE_SLUG] = slugify_text_title(text_title)
        row[self.COLUMN_DISSERTATION_TITLE] = row_dissertation_title
        
        # get date
        date_start = row[self.COLUMN_DISSERTATION_DATE_START]
        row[self.COLUMN_DISSERTATION_DATE_START] = ImportHelper.create_date_isoformat(date_start)
        date_end = row[self.COLUMN_DISSERTATION_DATE_END]
        row[self.COLUMN_DISSERTATION_DATE_END] = ImportHelper.create_date_isoformat(date_end)
        
        # get type
        row_dissertation_type = row[self.COLUMN_DISSERTATION_TYPE]
        dissertation_type = self.dissertation_import_helper.get_dissertation_type(row_dissertation_type)
        row[self.COLUMN_DISSERTATION_TYPE] = dissertation_type
        
        # check for duplicates
        [dissertation_key_exist, dissertation_duplicate_id] = self.dissertation_import_helper.check_dissertation_title(text_title) 
        dissertation_id = row[self.COLUMN_DISSERTATION_ID]
        if dissertation_key_exist:
            if dissertation_id == dissertation_duplicate_id:
                logger.warning('Dissertation update. Found dissertation with the same id: dissertation_title=' + text_title + ' dissertation_id=' + str(dissertation_id))
                import_report.warning(';'.join((self.REPORT_DISSERTATION_UPDATE, str(dissertation_id), text_title, row_dissertation_opi_id)))
            elif dissertation_id is not None:
                import_report.warning(';'.join((self.REPORT_DISSERTATION_NEW_EXIST_DUPLICATES, str(dissertation_id), text_title, row_dissertation_opi_id)))
                import_report.warning(';'.join((self.REPORT_DISSERTATION_DUPLICATE, str(dissertation_duplicate_id))))
                logger.warning(self.LOG_MSG_DUPLICATE_OBJECT)
                logger.warning('Existing object: dissertation_title=' + text_title + ' dissertation_id=' + str(dissertation_id))
                logger.warning('Duplicate object: ' + ' dissertation_id=' + str(dissertation_duplicate_id))
        else:
            import_report.info(';'.join((self.REPORT_DISSERTATION_NEW, str(dissertation_id), text_title, row_dissertation_opi_id)))
        return row
    
    # # overrided functions from Resource
    def skip_row(self, instance, original):
        if self._row_to_skip:
            logger.warning(self.get_skip_msg())
            import_report.warning(self.REPORT_SKIP_ROW + self.get_skip_msg())
            return True
        else:
            return super(DissertationResource, self).skip_row(instance, original)
            
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        
        self.ENTITY_IS_ACCEPTED = getattr(settings, "IMPORT_AUTO_PUBLICATION", False)
        
        # check columns set
        columns_set = {self.COLUMN_DISSERTATION_OPI_ID, self.COLUMN_DISSERTATION_TITLE, self.COLUMN_DISSERTATION_TYPE, self.COLUMN_DISSERTATION_DATE_START, self.COLUMN_DISSERTATION_DATE_END,
                                 self.COLUMN_DISSERTATION_INSTITUTION, self.COLUMN_DISSERTATION_AUTHOR, self.COLUMN_PERSON_DEGREE, self.COLUMN_PERSON_OPI_ID,
                                 self.COLUMN_PERSON_FIRST_NAME, self.COLUMN_PERSON_LAST_NAME, self.COLUMN_PERSON_FUNCTION}
        if not  set(dataset.headers) <= columns_set:
            logger.error(self.LOG_MSG_ERR_FILE_IMPROPER + ', '.join(columns_set))
            
        logger.info(self.LOG_MSG_IMPORT_BEGIN + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        import_report.info(self.REPORT_IMPORT_BEGIN + timezone.now().strftime('%B %d, %Y, %I:%M %p') + ';BIULETYN_ID ;TYTUŁ PRACY ;OPI_ID ;NAZWA INSTYTUCJI ')
        
        self.dissertation_import_helper = DissertationImportHelper.instance()
        
        return super(DissertationResource, self).before_import(dataset, using_transactions, dry_run, **kwargs)
    
    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        logger.info(self.LOG_MSG_IMPORT_END + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        import_report.info(self.REPORT_IMPORT_END + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        
        # clear memory
        if not dry_run:
            DissertationImportHelper.destroy_instance()
            
        return super(DissertationResource, self).after_import(dataset, result, using_transactions, dry_run, **kwargs)
    
    def before_import_row(self, row, **kwargs):
        
        self._row_to_skip = False  # by default row shouldn't be skipped
        
        is_dissertations_file = self.COLUMN_DISSERTATION_TYPE in row
        is_dissertations_people_file = self.COLUMN_PERSON_FUNCTION in row
        
        # get dissertation_id using opi_id
        [row, dissertation] = self.init_dissertation_row(row, is_dissertations_file)
        
        if is_dissertations_people_file:
            self.get_people_and_functions(row, dissertation)
        else:
            self.get_dissertation_data(row)
        
        return super(DissertationResource, self).before_import_row(row, **kwargs)
    
    def before_save_instance(self, instance, using_transactions, dry_run):
        instance.is_imported = True
        return super(DissertationResource, self).before_save_instance(instance, using_transactions, dry_run)
    
    def after_save_instance(self, instance, using_transactions, dry_run):
        if dry_run:
            return
               
        #update dissertations dictionary (to avoid query database)
        self.dissertation_import_helper.dissertations_ids_dict[instance.dissertation_id] = instance
        
        if instance.dissertation_institution is not None and instance.dissertation_institution not in instance.dissertation_authorizations.all():
            #add institution as authorized
            DissertationAuthorized.objects.create(dissertation=instance, authorized=instance.dissertation_institution)
        logger.info(self.LOG_MSG_ADDED_OBJECT + ("%d %s" % (instance.dissertation_id, instance.dissertation_title)))
        import_report.info(';'.join((self.REPORT_DISSERTATION_SAVED, str(instance.dissertation_id), instance.dissertation_title, str(instance.dissertation_opi_id))))

        return super(DissertationResource, self).after_save_instance(instance, using_transactions, dry_run)
    
    def import_data(self, dataset, dry_run=False, raise_errors=False, use_transactions=None, collect_failed_rows=False, **kwargs):
        if dry_run:
            logging.disable(logging.CRITICAL)
        else:
            logging.disable(logging.NOTSET)
        return super(DissertationResource, self).import_data(dataset, dry_run, raise_errors, use_transactions, collect_failed_rows, **kwargs)
    
    class Meta:
        fields = ('dissertation_type', 'dissertation_opi_id', 'dissertation_title_text', 'dissertation_date_start', 'dissertation_date_end',
                  'dissertation_institution', 'dissertation_reviewers',)
        import_id_fields = ('dissertation_id',)
        skip_unchanged = False
        report_skipped = True
        model = Dissertation
