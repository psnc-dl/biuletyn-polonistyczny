# -*- coding: utf-8 -*-
from builtins import RuntimeError
import datetime
import logging

from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator
from import_export import resources, fields

from bportal.module.common.utils import ImportHelper, slugify_text_title, SingletonMixin
from bportal.module.institution.models import Institution, InstitutionRole
from bportal.module.person.models import Person, ScientificTitle

from .models import Project, ProjectInstitution, ProjectParticipant, ProjectAuthorized


# Get an instance of a logger
logger = logging.getLogger(__name__)
import_report = logging.getLogger('projects_import_report')

class ProjectImportHelper(SingletonMixin):
    
    LOG_MSG_SUCC_DATABASE_CREATE_INST = "[CREATE] Create new institution object in database: "
    LOG_MSG_SUCC_DATABASE_GET_INST = "[UPDATE] Get institution object from database: "
    
    LOG_MSG_ERR_DATABASE_CREATE_INST = "[ERROR] Problem with create new institution object in database: "
    LOG_MSG_ERR_DATABASE_GET_INST = "[ERROR] On get institution object from database: "
    
    LOG_MSG_SUCC_DATABASE_GET_PROJ = "[UPDATE] Get project object from database: "
    LOG_MSG_ERR_DATABASE_GET_PROJ = "[ERROR] On get project object from database: "
    
    LOG_MSG_ERR_DATABASE_GET_PERSON = "[ERROR] On get person object from database: "
    
    REPORT_INSTITUTION_CREATED = 'Dodano instytucję'
    REPORT_INSTITUTION_UPDATED = 'Zaktualizowano instytucję'
    REPORT_INSTITUTION_CANNOT_CREATE = 'Nie można utworzyć instytucji'
    REPORT_INSTITUTION_NOT_FOUND = 'Nie znaleziono instytucji'
    REPORT_PERSON_NOT_FOUND = 'Nie znaleziono osoby'
    REPORT_PROJECT_NOT_FOUND = 'Nie znaleziono projektu'
    
    def __init__(self):
        # scientific titles
        self.MARK_PROF = 'prof'
        self.MARK_DR = 'dr'
        self.MARK_MGR = 'prof'
        scientific_titles = ScientificTitle.objects.all();
        self._prof_t = [t for t in scientific_titles if self.MARK_PROF in t.scientific_title_abbreviation][0]
        self._dr_t = [t for t in scientific_titles if self.MARK_DR in t.scientific_title_abbreviation][0]
        self._mgr_t = [t for t in scientific_titles if self.MARK_MGR in t.scientific_title_abbreviation][0]        
        
        institutions = Institution.objects.all();
        self.institutions_dict = dict((ImportHelper.create_dict_key(i.get_as_dict_key), i) for i in institutions)
        
        # people dictionary and set of ids
        people = Person.objects.all();
        self.people_ids = set(p.person_id for p in people)
        self.people_dict = dict((ImportHelper.create_dict_key(p.person_first_name, p.person_last_name), p.person_id) for p in people)
        self.people_ids_dict = dict((p.person_id, p) for p in people)
        self.dict_opi_id_person_id = dict((p.person_opi_id, p.person_id) for p in people)
        self.max_person_id = max(self.people_ids)
        
        # role
        self.MARK_DIRECTOR = 'kierow'
        self.MARK_MAIN_CONTRACTOR = 'główny'
        self.MARK_DOCTORAL = 'doktoran'
        
        # institution role
        self.MARK_INST_DIRECTOR = 'kier'
        self.MARK_INST_COWORK = 'wsp'
        self.MARK_INST_RELATED = 'powi'
        institution_roles = InstitutionRole.objects.all();
        self._roleinst_director = [r for r in institution_roles if self.MARK_INST_DIRECTOR in r.institution_role_role][0]
        self._roleinst_cowork = [r for r in institution_roles if self.MARK_INST_COWORK in r.institution_role_role][0]
        self._role_inst_related = [r for r in institution_roles if self.MARK_INST_RELATED in r.institution_role_role][0]
        
        # projects dictionary
        projects = list(Project.objects.all().prefetch_related("project_disciplines", "project_targets", "project_institutions", "project_participants", "project_person_participations"));
        self.projects_ids_dict = dict((p.project_id, p) for p in projects)
        self.projects_ids = set(p.project_id for p in projects)
        self.projects_opi_ids = set(p.project_opi_id for p in projects)
        self.dict_opi_id_project_id = dict((p.project_opi_id, p.project_id) for p in projects)
        self.max_project_id = max(self.projects_ids) if len(self.projects_ids) > 0 else 0
        self.projects_dict = dict((ImportHelper.create_dict_key(p.project_title_text), p.project_id) for p in projects)
        
        # cache
        self.all_participants = list(ProjectParticipant.objects.filter(is_principal=False))
        self.all_directors = list(ProjectParticipant.objects.filter(is_principal=True))
        self.projects_participants = {}
        self.projects_directors = {}
        
        for pp in self.all_participants:
            if pp.project.project_id not in self.projects_participants:
                self.projects_participants[pp.project.project_id] = [pp.person.person_id]
            else:
                self.projects_participants[pp.project.project_id].append(pp.person.person_id)
        
        for pp in self.all_directors:
            if pp.project.project_id not in self.projects_directors:
                self.projects_directors[pp.project.project_id] = [pp.person.person_id]
            else:
                self.projects_directors[pp.project.project_id].append(pp.person.person_id)
              
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
        [_, proposed_id] = self.check_person_opi_id(row_person_opi_id)
         
        return proposed_id
    
    def get_project_id(self, row_project_opi_id):
        [opi_id_exist, proposed_id] = self.check_project_opi_id(row_project_opi_id)
        if opi_id_exist:
            return [opi_id_exist, proposed_id]
         
        proposed_id = self.max_project_id + 1
        while ((proposed_id in self.projects_ids) and (proposed_id > 0)):
            self.max_project_id += 1
            proposed_id = self.max_project_id
        self.projects_ids.add(proposed_id)
        
        return [opi_id_exist, proposed_id]
    
    def check_project_opi_id(self, proposed_opi_id):
        proposed_opi_id = int(proposed_opi_id)
        opi_id_exist = proposed_opi_id in self.projects_opi_ids
        project_id = self.dict_opi_id_project_id.get(proposed_opi_id, None)
        return [opi_id_exist, project_id]
    
    def check_person_opi_id(self, proposed_opi_id):
        if not proposed_opi_id:
            return [False, None]
        
        proposed_opi_id = int(proposed_opi_id)
        opi_id_exist = proposed_opi_id in self.dict_opi_id_person_id
        person_id = self.dict_opi_id_person_id.get(proposed_opi_id, None)
        return [opi_id_exist, person_id]
    
    def check_project_title(self, ptitle):
        project_key = ImportHelper.create_dict_key(ptitle)
        project_id = None
        project_key_exist = project_key in self.projects_dict
        if project_key_exist:
            project_id = self.projects_dict[project_key]
        return [project_key_exist, project_id]
    
    # person role checkers
    def is_contractor(self, row_person_function):
        if row_person_function is None:
            return False
        if self.MARK_CONTRACTOR in row_person_function:
            return True
        else:
            return False
    
    def is_director(self, row_person_function):
        if row_person_function is None:
            return False
        if self.MARK_DIRECTOR in row_person_function:
            return True
        else:
            return False
        
    def is_doctoral_candidate(self, row_person_function):
        if row_person_function is None:
            return False
        if self.MARK_DOCTORAL in row_person_function:
            return True
        else:
            return False
        
    def get_institutions_for_project(self, project):
        if project is None:
            return []
        institutions = list(project.project_institutions.all())
        return institutions
    
    # people getters by role
    def get_participants(self, project):
        if project is None:
            return []
        participants = []
        if project.project_id in self.projects_participants:
            participants = self.projects_participants[project.project_id]
            logger.info('loaded cache participants dict for project id=' + str(project.project_id))
        return participants
    
    def get_directors(self, project):
        if project is None:
            return []
        directors = []
        if project.project_id in self.projects_directors:
            directors = self.projects_directors[project.project_id]
            logger.info('loaded cache directors dict for project id=' + str(project.project_id))
        return directors
    
    
    def get_project_object(self, project_id):
        project = None
        if (project_id in self.projects_ids_dict):
            try:
                project = self.projects_ids_dict[project_id]
                logger.info(self.LOG_MSG_SUCC_DATABASE_GET_PROJ + ' get_project_object ' + ' project_id=' + str(project_id))
            except Exception:
                logger.error(self.LOG_MSG_ERR_DATABASE_GET_PROJ + ' get_project_object ' + ' project_id=' + str(project_id))
                import_report.error(';'.join((self.REPORT_PROJECT_NOT_FOUND, str(project_id))))
        return project
    
    def try_get_project_object(self, row_project_opi_id):
        [opi_id_exists, project_id] = self.get_project_id(row_project_opi_id)
        project = None
        if opi_id_exists:
            project = self.get_project_object(project_id)
        return [project, project_id]
    
    def get_person_object(self, person_id):
        person = None
        if person_id in self.people_ids_dict:
            try:
                person = self.people_ids_dict[person_id]
                return person
            except Exception:
                logger.error(self.LOG_MSG_ERR_DATABASE_GET_PERSON + ' get_person_object person_id=' + str(person_id))
                import_report.error(';'.join((self.REPORT_PERSON_NOT_FOUND, str(person_id))))
        raise RuntimeError(self.REPORT_PERSON_NOT_FOUND)
    
       
class ProjectResource(resources.ModelResource):
    COLUMN_PROJECT_ID = 'TMP_PROJECT_ID'
    COLUMN_PROJECT_OPI_ID = 'PRACE_BADAWCZE_ID'
    COLUMN_PROJECT_TITLE = 'TYTUL'
    COLUMN_PROJECT_TITLE_SLUG = 'TMP_TITLE_SLUG'
    COLUMN_PROJECT_TITLE_TEXT = 'TMP_TITLE_TEXT'
    COLUMN_PROJECT_TYPE = 'RODZAJ_PRACY'
    COLUMN_PROJECT_PARTICIPANTS = 'TMP_PROJECT_PARTICIPANTS'
    COLUMN_PROJECT_DATE_START = 'DATA_ROZPOCZECIA'
    COLUMN_PROJECT_DATE_END = 'DATA_ZAKONCZENIA'
    COLUMN_PROJECT_INSTITUTIONS = 'NAZWA_INST'
    COLUMN_PROJECT_IS_ACCEPTED = 'TMP_PROJECT_IS_ACCEPTED'
    
    # columns for people-projects associations
    COLUMN_PERSON_FUNCTION = 'FUNKCJA_OSOBY'
    COLUMN_PERSON_OPI_ID = 'OSOBY_ID'
    COLUMN_PERSON_FIRST_NAME = 'IMIE'
    COLUMN_PERSON_LAST_NAME = 'NAZWISKO'
    COLUMN_PERSON_DEGREE = 'STOPIEN'
    
    project_id = fields.Field(column_name=COLUMN_PROJECT_ID, attribute='project_id')
    project_opi_id = fields.Field(column_name=COLUMN_PROJECT_OPI_ID, attribute='project_opi_id')
    project_title = fields.Field(column_name=COLUMN_PROJECT_TITLE, attribute='project_title')
    project_title_text = fields.Field(column_name=COLUMN_PROJECT_TITLE_TEXT, attribute='project_title_text')
    project_title_slug = fields.Field(column_name=COLUMN_PROJECT_TITLE_SLUG, attribute='project_title_slug')
    project_date_start = fields.Field(column_name=COLUMN_PROJECT_DATE_START, attribute='project_date_start')
    project_date_end = fields.Field(column_name=COLUMN_PROJECT_DATE_END, attribute='project_date_end')
    project_is_accepted = fields.Field(column_name=COLUMN_PROJECT_IS_ACCEPTED, attribute='project_is_accepted')
    
    # implemented using proper m2m managers due to intermediary model
    project_participants = fields.Field(column_name=COLUMN_PROJECT_PARTICIPANTS)
    project_institutions = fields.Field(column_name=COLUMN_PROJECT_INSTITUTIONS)
    
    # fields not used but included into import file
    project_type = fields.Field(column_name=COLUMN_PROJECT_TYPE)
    
    person_function = fields.Field(column_name=COLUMN_PERSON_FUNCTION)
    person_opi_id = fields.Field(column_name=COLUMN_PERSON_OPI_ID)
    person_first_name = fields.Field(column_name=COLUMN_PERSON_FIRST_NAME)
    person_last_name = fields.Field(column_name=COLUMN_PERSON_LAST_NAME)
    person_degree = fields.Field(column_name=COLUMN_PERSON_DEGREE)
    
    LOG_MSG_ERR_FILE_IMPROPER = "[ERROR] Not proper input file for import Project objects. Please check if following columns exist: "
    LOG_MSG_ADDED_OBJECT = "[SUCCESS] Project object has been successfully saved. "
    LOG_MSG_DUPLICATE_OBJECT = "[DUPLICATE] Project object potentially duplicated: "
    LOG_MSG_IMPORT_BEGIN = "[STARTED IMPORT] --- IMPORT PROJECTS PROCESS INITIALIZED --- "
    LOG_MSG_IMPORT_END = "[FINISHED IMPORT] --- IMPORT PROJECTS PROCESS FINISHED --- "
    LOG_MSG_ADDED_OBJECT = "[SUCCESS] Project object has been successfully saved. "
    LOG_MSG_ERROR_MISSING_PROJECT = "[NOT FOUND OBJECT] Project object not found in database! "
    LOG_MSG_ERROR_MISSING_PERSON = "[NOT FOUND OBJECT] Person object not found in database! "
    
    REPORT_FILE_IMPROPER = 'Nie poprawny format pliku dla importu projektów. Sprawdź czy plik zawiera następujące kolumny:'
    REPORT_IMPORT_BEGIN = '--- -- - POCZĄTEK IMPORTU - -- ---'
    REPORT_IMPORT_END = '--- -- - KONIEC IMPORTU - -- ---'
    REPORT_PROJECT_NEW = 'Nowy projekt'
    REPORT_PROJECT_NEW_EXIST_DUPLICATES = 'Nowy projekt. Istnieją potencjalne duplikaty'
    REPORT_PROJECT_SAVED = 'Zapisano projekt'
    REPORT_PROJECT_UPDATE = 'Aktualizacja projektu. Znaleziono projekt o takim samym ID.'
    REPORT_PROJECT_DUPLICATE = 'Potencjalny duplikat projektu'
    REPORT_PROJECT_DIRECTOR = 'Kierownik projektu'
    REPORT_PROJECT_PARTICIPANT = 'Uczestnik projektu'
    REPORT_INSTITUTION_COWORK = 'Instytucja biorąca udział w projekcie'
    REPORT_INSTITUTION_DIRECTOR = 'Instytucja kierująca projektem'
    REPORT_SKIP_ROW = 'Pominięto wiersz'
    
    def __init__(self):
        # initialize import helper
        self._row_to_skip = False
        self._skip_msg = '[SKIPPED ROW]'
        self._resource_info = ''
        self.ENTITY_IS_ACCEPTED = False
        self.institutions = None
        self.participants = None
        self.directors = None
        self.participants_to_add = []
        self.directors_to_add = []
        
        self.existing_project_institutions = []
    
    def create_resource_info(self, row):
        return '[SKIPPED ROW] [' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] ' + '; '.join('{}={}'.format(k, v) for k, v in row.items())
    
    def get_skip_msg(self):
        return self._skip_msg
    
    def mark_row_to_skip(self, row=dict(), reason_msg=''):
        self._row_to_skip = True
        self._skip_msg = reason_msg + self.create_resource_info(row)
    
    def init_project_row(self, row, is_projects_file):
        row_project_opi_id = row.get(self.COLUMN_PROJECT_OPI_ID, '')
        [project, project_id] = self.project_import_helper.try_get_project_object(row_project_opi_id)
        row[self.COLUMN_PROJECT_ID] = project_id
    
        if project is None:
            if (is_projects_file):
                row[self.COLUMN_PROJECT_PARTICIPANTS] = None
                row[self.COLUMN_PROJECT_IS_ACCEPTED] = self.ENTITY_IS_ACCEPTED
                
            else:
                #row[self.COLUMN_PROJECT_OPI_ID] = None
                row[self.COLUMN_PROJECT_TITLE] = row[self.COLUMN_PERSON_FIRST_NAME] + ' ' + row[self.COLUMN_PERSON_LAST_NAME]
                row[self.COLUMN_PROJECT_TYPE] = None
                row[self.COLUMN_PROJECT_DATE_START] = None
                row[self.COLUMN_PROJECT_DATE_END] = None
                row[self.COLUMN_PROJECT_INSTITUTIONS] = None
                self.mark_row_to_skip(row, self.LOG_MSG_ERROR_MISSING_PROJECT)  # #NOTE: there is no information about project in projects-people file
        else:
            if (is_projects_file):
                row[self.COLUMN_PROJECT_PARTICIPANTS] = project.project_participants
                row[self.COLUMN_PROJECT_IS_ACCEPTED] = project.project_is_accepted
            else:
                row[self.COLUMN_PROJECT_OPI_ID] = project.project_opi_id
                row[self.COLUMN_PROJECT_TITLE] = project.project_title
                row[self.COLUMN_PROJECT_TITLE_SLUG] = project.project_title_slug
                row[self.COLUMN_PROJECT_TITLE_TEXT] = project.project_title_text
                # row[self.COLUMN_PROJECT_TYPE] = project.project_type
                row[self.COLUMN_PROJECT_DATE_START] = project.project_date_start
                row[self.COLUMN_PROJECT_DATE_END] = project.project_date_end
                row[self.COLUMN_PROJECT_INSTITUTIONS] = None #will be assigned after save instance
            
        return [row, project]
    
    def get_people_and_functions(self, row, project):
        # get person_id using opi_id
        row_person_opi_id = row.get(self.COLUMN_PERSON_OPI_ID, '')
        person_id = self.project_import_helper.get_person_id(row_person_opi_id)
        self.participants = self.project_import_helper.get_participants(project)
        self.directors = self.project_import_helper.get_directors(project)
        self.participants_to_add = []
        self.directors_to_add = []
        self.institutions = self.project_import_helper.get_institutions_for_project(project)
        
        if person_id is None:
            self.mark_row_to_skip(row, self.LOG_MSG_ERROR_MISSING_PERSON)  # #NOTE: there is no information about person in projects-people file
        
        row_project_person_function = row.get(self.COLUMN_PERSON_FUNCTION, '')
        if row_project_person_function:
            if self.project_import_helper.is_director(row_project_person_function):
                if person_id not in self.directors:
                    self.directors_to_add.append(person_id)
            else:
                if person_id not in self.participants:
                    self.participants_to_add.append(person_id)
            row[self.COLUMN_PROJECT_PARTICIPANTS] = None  # it will be rewrite after save instance
           
        return row
    
    def get_project_data(self, row):
        # get project_institutions
        row_project_institutions = row.get(self.COLUMN_PROJECT_INSTITUTIONS, '')
        if isinstance(row_project_institutions, str):
            self.institutions = self.project_import_helper.get_institutions(row_project_institutions)
        else:
            self.institutions = row_project_institutions
            
        row[self.COLUMN_PROJECT_INSTITUTIONS] = None  # it will be rewrite after save instance                      
        
        # get project_title ant title_slug
        row_project_opi_id = row.get(self.COLUMN_PROJECT_OPI_ID, '')
        row_project_title = row.get(self.COLUMN_PROJECT_TITLE, '')
        text_title = strip_tags(row_project_title)
        row[self.COLUMN_PROJECT_TITLE_TEXT] = text_title
        row[self.COLUMN_PROJECT_TITLE_SLUG] = slugify_text_title(text_title)
        row[self.COLUMN_PROJECT_TITLE] = row_project_title
        
        # get date
        date_start = row[self.COLUMN_PROJECT_DATE_START]
        row[self.COLUMN_PROJECT_DATE_START] = ImportHelper.create_date_isoformat(date_start)
        date_end = row[self.COLUMN_PROJECT_DATE_END]
        row[self.COLUMN_PROJECT_DATE_END] = ImportHelper.create_date_isoformat(date_end)
        
        # check for duplicates
        [project_key_exist, project_duplicate_id] = self.project_import_helper.check_project_title(text_title) 
        project_id = row[self.COLUMN_PROJECT_ID]
        if project_key_exist:
            if project_id == project_duplicate_id:
                logger.warning('Project update. Found project with the same id: project_title=' + text_title + ' project_id=' + str(project_id))
                import_report.warning(';'.join((self.REPORT_PROJECT_UPDATE, str(project_id), text_title, str(row_project_opi_id))))
            elif project_id is not None: 
                logger.warning(self.LOG_MSG_DUPLICATE_OBJECT)
                logger.warning('Existing object: project_title=' + text_title + ' project_id=' + str(project_id))
                logger.warning('Duplicate object: ' + ' project_id=' + str(project_duplicate_id))
                import_report.warning(';'.join((self.REPORT_PROJECT_NEW_EXIST_DUPLICATES, str(project_id), text_title, str(row_project_opi_id))))
                import_report.warning(';'.join((self.REPORT_PROJECT_DUPLICATE, str(project_duplicate_id))))
        else:
            import_report.info(';'.join((self.REPORT_PROJECT_NEW, str(project_id), text_title)))   
#         ##get project type TODO: check if it will be used?
#         row_project_type = row[self.COLUMN_PROJECT_TYPE]
#         project_type = self.project_import_helper.get_project_type(row_project_type)
#         row[self.COLUMN_PROJECT_TYPE] = project_type

        return row
    
    # # overrided functions from Resource
    def skip_row(self, instance, original):
        if self._row_to_skip:
            logger.warning(self.get_skip_msg())
            import_report.warning(self.REPORT_SKIP_ROW + self.get_skip_msg())
            return True
        else:
            return super(ProjectResource, self).skip_row(instance, original)
    
    def before_import_row(self, row, **kwargs):
        self._row_to_skip = False  # by default row shouldn't be skipped
        
        is_projects_file = self.COLUMN_PROJECT_TYPE in row
        is_projects_people_file = self.COLUMN_PERSON_FUNCTION in row
        
        # get project_id using opi_id
        [row, project] = self.init_project_row(row, is_projects_file)
        
        if project is not None:
            self.existing_project_institutions = list(project.project_institutions.all())
            
        if is_projects_people_file:
            self.get_people_and_functions(row, project)
        else:
            self.get_project_data(row)
        
        return super(ProjectResource, self).before_import_row(row, **kwargs)
    
    def before_save_instance(self, instance, using_transactions, dry_run):
        instance.is_imported = True
        return super(ProjectResource, self).before_save_instance(instance, using_transactions, dry_run)
    
    def after_save_instance(self, instance, using_transactions, dry_run):
        if dry_run:
            return
        if self.institutions is not None:
            if len(self.institutions) > 0:
                if self.institutions[0] not in self.existing_project_institutions:
                    pinst = ProjectInstitution()
                    pinst.project = instance
                    pinst.institution = self.institutions[0]
                    pinst.role = self.project_import_helper._roleinst_director
                    pinst.save()
                    logger.info(self.REPORT_INSTITUTION_DIRECTOR + ("%d %s" % (pinst.institution.institution_id, pinst.institution.institution_fullname)))
                    #add institution as authorized
                    ProjectAuthorized.objects.create(project=instance, authorized=self.institutions[0])

                for i in self.institutions[1:]:
                    if i not in self.existing_project_institutions:
                        pinst = ProjectInstitution()
                        pinst.project = instance
                        pinst.institution = i
                        pinst.role = self.project_import_helper._roleinst_cowork
                        pinst.save()
                        logger.info(self.REPORT_INSTITUTION_COWORK + ("%d %s" % (pinst.institution.institution_id, pinst.institution.institution_fullname)))
                        import_report.info(';'.join((self.REPORT_INSTITUTION_COWORK, str(pinst.institution.institution_id), pinst.institution.institution_fullname, '')))
                        #add institution as authorized
                        ProjectAuthorized.objects.create(project=instance, authorized=i)
        try:
            if self.directors_to_add is not None:
                for person_id in self.directors_to_add:
                    pp = ProjectParticipant()
                    pp.project = instance
                    pp.person = self.project_import_helper.get_person_object(person_id)
                    pp.is_principal = True
                    pp.save()
                    logger.info(self.REPORT_PROJECT_DIRECTOR + ("%d %s" % (pp.person.person_id, pp.person.person_first_name + pp.person.person_last_name)))
                    import_report.info(';'.join((self.REPORT_PROJECT_DIRECTOR, str(pp.person.person_id), pp.person.person_first_name + pp.person.person_last_name, str(pp.person.person_opi_id))))
            if self.directors is not None and not dry_run:
                self.directors.extend(self.directors_to_add)
                self.project_import_helper.projects_directors[instance.project_id] = self.directors
                    
            if self.participants_to_add is not None:
                for person_id in self.participants_to_add:
                    pp = ProjectParticipant()
                    pp.project = instance
                    pp.person = self.project_import_helper.get_person_object(person_id)
                    pp.save()
                    logger.info(self.REPORT_PROJECT_PARTICIPANT + ("%d %s" % (pp.person.person_id, pp.person.person_first_name + pp.person.person_last_name)))
                    import_report.info(';'.join((self.REPORT_PROJECT_PARTICIPANT, str(pp.person.person_id), pp.person.person_first_name + pp.person.person_last_name, str(pp.person.person_opi_id))))
            if self.participants is not None:
                self.participants.extend(self.participants_to_add)
                self.project_import_helper.projects_participants[instance.project_id] = self.participants    
        except RuntimeError as e:
            logger.error(self.LOG_MSG_ERROR_MISSING_PERSON + ("%d %s" % (instance.project_id, instance.project_title)))
            import_report.error(';'.join((e.message, str(instance.project_id), instance.project_title, str(instance.project_opi_id), str(person_id))))
        logger.info(self.LOG_MSG_ADDED_OBJECT + ("%d %s" % (instance.project_id, instance.project_title)))
        import_report.info(';'.join((self.REPORT_PROJECT_SAVED, str(instance.project_id), instance.project_title, str(instance.project_opi_id))))
              
        return super(ProjectResource, self).after_save_instance(instance, using_transactions, dry_run)
    
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.project_import_helper = ProjectImportHelper.instance()
        
        self.ENTITY_IS_ACCEPTED = getattr(settings, "IMPORT_AUTO_PUBLICATION", False)
        
        # check columns set
        columns_set = {self.COLUMN_PROJECT_OPI_ID, self.COLUMN_PROJECT_TITLE, self.COLUMN_PROJECT_DATE_END, self.COLUMN_PROJECT_DATE_START, self.COLUMN_PROJECT_TYPE,
                                 self.COLUMN_PROJECT_INSTITUTIONS, self.COLUMN_PERSON_DEGREE, self.COLUMN_PERSON_OPI_ID,
                                 self.COLUMN_PERSON_FIRST_NAME, self.COLUMN_PERSON_LAST_NAME, self.COLUMN_PERSON_FUNCTION}
        if not  set(dataset.headers) <= columns_set:
            logger.error(self.LOG_MSG_ERR_FILE_IMPROPER + ', '.join(columns_set))     
        logger.info(self.LOG_MSG_IMPORT_BEGIN + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        import_report.info(self.REPORT_IMPORT_BEGIN + timezone.now().strftime('%B %d, %Y, %I:%M %p') + ';BIULETYN_ID ;NAZWA;OPI_ID ;')
        return super(ProjectResource, self).before_import(dataset, using_transactions, dry_run, **kwargs)
    
    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        # clear memory
        if not dry_run:
            ProjectImportHelper.destroy_instance()
        
        logger.info(self.LOG_MSG_IMPORT_END + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        import_report.info(self.REPORT_IMPORT_END + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        return super(ProjectResource, self).after_import(dataset, result, using_transactions, dry_run, **kwargs)
    
    def import_data(self, dataset, dry_run=False, raise_errors=False, use_transactions=None, collect_failed_rows=False, **kwargs):
        if dry_run:
            logging.disable(logging.CRITICAL)
        else:
            logging.disable(logging.NOTSET)
        return super(ProjectResource, self).import_data(dataset, dry_run, raise_errors, use_transactions, collect_failed_rows, **kwargs)
    
    class Meta:
        fields = ('project_type', 'project_opi_id', 'project_title_text', 'project_title', 'project_date_start', 'project_date_end', 'project_institutions')
        import_id_fields = ('project_id',)
        skip_unchanged = False
        report_skipped = True
        model = Project
