# -*- coding: utf-8 -*-
import logging

from django.utils import timezone
from django.utils.text import Truncator
from import_export import resources, fields

from bportal.module.common.models import ResearchDiscipline
from bportal.module.common.utils import ImportHelper, SingletonMixin
from bportal.module.common.utils import slugify_text_title
from bportal.module.institution.models import Institution

from .models import ScientificTitle, Person, PersonAffiliation


# Get an instance of a logger
logger = logging.getLogger(__name__)
import_report = logging.getLogger('people_import_report')


class PersonImportHelper(SingletonMixin):
    
    LOG_MSG_SUCC_DATABASE_CREATE_INST = "[CREATE] Create new institution object in database: "
    LOG_MSG_SUCC_DATABASE_CREATE_DISC = "[CREATE] Create new research discipline object in database: "
    
    REPORT_INSTITUTION_CREATED = 'Dodano instytucję'
    REPORT_INSTITUTION_UPDATED = 'Zaktualizowano instytucję'
    REPORT_DISCIPLINE_CREATED = 'Dodano dyscyplinę naukową'

    def __init__(self):
                
        # scientific titles
        self.MARK_PROF = 'prof'
        self.MARK_DR = 'dr'
        self.MARK_MGR = 'prof'
        
        scientific_titles = list(ScientificTitle.objects.all());
        self._prof_t = [t for t in scientific_titles if self.MARK_PROF in t.scientific_title_abbreviation][0]
        self._dr_t = [t for t in scientific_titles if self.MARK_DR in t.scientific_title_abbreviation][0]
        self._mgr_t = [t for t in scientific_titles if self.MARK_MGR in t.scientific_title_abbreviation][0]
        
        institutions = list(Institution.objects.all());
        self.institutions_dict = dict((ImportHelper.create_dict_key(i.get_as_dict_key), i) for i in institutions)
        
        disciplines = list(ResearchDiscipline.objects.all());
        self.disciplines_dict = dict((ImportHelper.create_dict_key(d.discipline_fullname), d) for d in disciplines)
                
        # people dictionary and set of ids
        people = list(Person.objects.all().prefetch_related('person_disciplines'));
        print(len(people))
        self.people_dict = dict((ImportHelper.create_dict_key(p.person_first_name, p.person_last_name), p.person_id) for p in people)
        self.people_ids = list(p.person_id for p in people)
        self.people_opi_ids = list(p.person_opi_id for p in people)
        self.dict_opi_id_person_id = dict((p.person_opi_id, p.person_id) for p in people)
        self.max_person_id = max(self.people_ids)
        
        # cache
        affiliations = list(PersonAffiliation.objects.filter(is_principal=False).select_related('institution', 'person'))
        principal_affiliations = list(PersonAffiliation.objects.filter(is_principal=True).select_related('institution', 'person'))
        self.person_affiliations = {}
        self.person_principal_affiliations = {}
        self.person_disciplines = {}
        
        for pa in affiliations:
            if pa.person.person_id not in self.person_affiliations:
                self.person_affiliations[pa.person.person_id] = [pa.institution.institution_id]
            else:
                self.person_affiliations[pa.person.person_id].append(pa.institution.institution_id)
        
        for pa in principal_affiliations:
            if pa.person.person_id not in self.person_principal_affiliations:
                self.person_principal_affiliations[pa.person.person_id] = [pa.institution.institution_id]
            else:
                self.person_principal_affiliations[pa.person.person_id].append(pa.institution.institution_id)
        
        for p in people:
            self.person_disciplines[p.person_id] = list(p.person_disciplines.all())
                        
    def get_principal_affiliation(self, person_id):
        if person_id in self.person_principal_affiliations:
            return self.person_principal_affiliations[person_id]
        else:
            return []
     
    def get_affiliations(self, person_id):
        if person_id in self.person_affiliations:
            return self.person_affiliations[person_id]
        else:
            return []
    
    def get_person_disciplines(self, person_id):
        if person_id in self.person_disciplines:
            return self.person_disciplines[person_id]
        else:
            return []
               
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
    
    def get_or_create_discipline_object(self, discipline_name):
        discipline = None
        discipline_key = ImportHelper.create_dict_key(discipline_name)
        if (discipline_key not in self.disciplines_dict):
            discipline = ResearchDiscipline.objects.create(discipline_fullname=discipline_name.capitalize())
            self.disciplines_dict[discipline_key] = discipline
            logger.info(self.LOG_MSG_SUCC_DATABASE_CREATE_DISC + 'get_or_create_discipline_object discipline_name=' + discipline_name + ' discipline_id=' + str(discipline.discipline_id))
            import_report.info(';'.join((self.REPORT_DISCIPLINE_CREATED, str(discipline.discipline_id), '', '', '', discipline_name)))
        else:
            discipline = self.disciplines_dict[discipline_key]
        return discipline
        
    def get_disciplines(self, disciplines_names_str):
        disciplines = list()
        if disciplines_names_str:
            disciplines_names_arr = disciplines_names_str.split('/')
            for discipline_name in disciplines_names_arr:
                discipline_name = discipline_name.strip()
                if not discipline_name:
                    continue
                discipline = self.get_or_create_discipline_object(discipline_name)
                disciplines.append(discipline)
        return disciplines      
    
    def get_person_id(self, row_person_opi_id):
        [_, proposed_id] = self.check_person_opi_id(row_person_opi_id)
        
        return proposed_id
    
    def check_person_opi_id(self, proposed_opi_id):
        proposed_opi_id = int(proposed_opi_id)
        opi_id_exist = proposed_opi_id in self.people_opi_ids
        person_id = self.dict_opi_id_person_id.get(proposed_opi_id, None)
        return [opi_id_exist, person_id]
    
    def check_person_name(self, fname, lname):
        person_key = ImportHelper.create_dict_key(fname, lname)
        person_id = None
        person_key_exist = person_key in self.people_dict
        if person_key_exist:
            person_id = self.people_dict[person_key]
        return [person_key_exist, person_id]


class PersonResource(resources.ModelResource):
    COLUMN_PERSON_ID = 'PERSON_ID'
    COLUMN_PERSON_OPI_ID = 'OSOBY_ID'
    COLUMN_PERSON_TITLE = 'STOPIEN_NAUKOWY'
    COLUMN_PERSON_INSTITUTIONS = 'ETATY'
    COLUMN_PERSON_FIRST_NAME = 'IMIE'
    COLUMN_PERSON_LAST_NAME = 'NAZWISKO'
    COLUMN_PERSON_EMAIL = 'MAIL'
    COLUMN_PERSON_SLUG = 'PERSON_SLUG'
    COLUMN_PERSON_KBN = 'KBN_RAZEM'
    COLUMN_PERSON_SPEC = 'SPEC_RAZEM'
    COLUMN_PERSON_FOREIGNER = 'OSOBA_ZAGRANICZNA'
    COLUMN_PERSON_DIED = 'ZMARL'    
    
    person_id = fields.Field(column_name=COLUMN_PERSON_ID, attribute='person_id')
    person_opi_id = fields.Field(column_name=COLUMN_PERSON_OPI_ID, attribute='person_opi_id')
    person_first_name = fields.Field(column_name=COLUMN_PERSON_FIRST_NAME, attribute='person_first_name')
    person_last_name = fields.Field(column_name=COLUMN_PERSON_LAST_NAME, attribute='person_last_name')
    person_title = fields.Field(column_name=COLUMN_PERSON_TITLE, attribute='person_title')
    person_slug = fields.Field(column_name=COLUMN_PERSON_SLUG, attribute='person_slug')
    person_institutions = fields.Field(column_name=COLUMN_PERSON_INSTITUTIONS)
    person_email = fields.Field(column_name=COLUMN_PERSON_EMAIL, attribute='person_email')
    person_kbn = fields.Field(column_name=COLUMN_PERSON_KBN)
    # fields not used but included into import file
    person_spec = fields.Field(column_name=COLUMN_PERSON_SPEC)
    person_foreigner = fields.Field(column_name=COLUMN_PERSON_FOREIGNER)
    person_died = fields.Field(column_name=COLUMN_PERSON_DIED)
    
    LOG_MSG_ERR_FILE_IMPROPER = "[ERROR] Not proper input file for import Person objects. Please check if following columns exist: "
    LOG_MSG_ADDED_OBJECT = "[SUCCESS] Person object has been successfully saved: "
    LOG_MSG_DUPLICATE_OBJECT = "[DUPLICATE] Person object potentially duplicated: "
    LOG_MSG_IMPORT_BEGIN = "[STARTED IMPORT] --- IMPORT PEOPLE PROCESS INITIALIZED --- "
    LOG_MSG_IMPORT_END = "[FINISHED IMPORT] --- IMPORT PEOPLE PROCESS FINISHED --- "
    
    REPORT_FILE_IMPROPER = 'Nie poprawny format pliku dla importu osób. Sprawdź czy plik zawiera następujące kolumny:'
    REPORT_IMPORT_BEGIN = '--- -- - POCZĄTEK IMPORTU - -- ---'
    REPORT_IMPORT_END = '--- -- - KONIEC IMPORTU - -- ---'
    REPORT_PERSON_NEW = 'Nowa osoba'
    REPORT_PERSON_NEW_EXIST_DUPLICATES = 'Nowa osoba. Istnieją potencjalne duplikaty' 
    REPORT_PERSON_SAVED = 'Zapisano osobę'
    REPORT_PERSON_UPDATE = 'Aktualizacja osoby. Znaleziono osobę o takim samym ID.'
    REPORT_PERSON_DUPLICATE = 'Potencjalny duplikat osoby'
    
       
    def dehydrate_person_slug(self, person):
        return '%s' % slugify_text_title(person.person_first_name + ' ' + person.person_last_name)
    
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        logger.info('CACHE INITIALIZAION STARTED' + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        self.person_import_helper = PersonImportHelper.instance()
        logger.info('CACHE INITIALIZATOIN FINISHED' + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        
        # check columns set
        columns_set = {self.COLUMN_PERSON_OPI_ID, self.COLUMN_PERSON_FIRST_NAME, self.COLUMN_PERSON_LAST_NAME, self.COLUMN_PERSON_INSTITUTIONS,
                                 self.COLUMN_PERSON_EMAIL, self.COLUMN_PERSON_KBN, self.COLUMN_PERSON_SPEC, self.COLUMN_PERSON_FOREIGNER, self.COLUMN_PERSON_DIED}
        if not  columns_set <= set(dataset.headers):
            logger.error(self.LOG_MSG_ERR_FILE_IMPROPER + ', '.join(columns_set))
            import_report.error(self.REPORT_FILE_IMPROPER + ', '.join(columns_set))
        logger.info(self.LOG_MSG_IMPORT_BEGIN + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        import_report.info(self.REPORT_IMPORT_BEGIN + timezone.now().strftime('%B %d, %Y, %I:%M %p') + ';BIULETYN_ID ;IMIĘ ;NAZWISKO ;OPI_ID ;NAZWA INSTYTUCJI ')

        return super(PersonResource, self).before_import(dataset, using_transactions, dry_run, **kwargs)
    
    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        
        # clear memory
        if not dry_run:
            PersonImportHelper.destroy_instance()
        
        logger.info(self.LOG_MSG_IMPORT_END + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        import_report.info(self.REPORT_IMPORT_END + timezone.now().strftime('%B %d, %Y, %I:%M %p'))
        
        return super(PersonResource, self).after_import(dataset, result, using_transactions, dry_run, **kwargs)
    
    def before_import_row(self, row, **kwargs):
        
        # get scientific title instance
        row_person_title = row.get(self.COLUMN_PERSON_TITLE, '')
        row[self.COLUMN_PERSON_TITLE] = self.person_import_helper.get_scientific_title(row_person_title)
        
        # get person_id using opi_id
        row_person_opi_id = row.get(self.COLUMN_PERSON_OPI_ID, '')
        person_id = self.person_import_helper.get_person_id(row_person_opi_id)
        row[self.COLUMN_PERSON_ID] = person_id
        
        # get person_institutions
        row_person_institutions = row.get(self.COLUMN_PERSON_INSTITUTIONS, '')
        self.institutions = self.person_import_helper.get_institutions(row_person_institutions)
        row[self.COLUMN_PERSON_INSTITUTIONS] = None  # it will be set in after_save_instance method                  
        
        # get person_disciplines
        row_person_disciplines = row.get(self.COLUMN_PERSON_KBN, '')
        self.disciplines = self.person_import_helper.get_disciplines(row_person_disciplines)
        row[self.COLUMN_PERSON_KBN] = None  # it will be set in after_save_instance method   
        
        # get person_slug
        fname = row.get(self.COLUMN_PERSON_FIRST_NAME, '')
        lname = row.get(self.COLUMN_PERSON_LAST_NAME, '')
        row[self.COLUMN_PERSON_SLUG] = slugify_text_title(fname + ' ' + lname)
        
        [person_key_exist, person_duplicate_id] = self.person_import_helper.check_person_name(fname, lname) 
        if person_key_exist:
            if person_id == person_duplicate_id:
                logger.warning('Person update. Found person with the same id: person_name=' + fname + ' ' + lname + ' person_id=' + str(person_id))
                import_report.warning(';'.join((self.REPORT_PERSON_UPDATE, str(person_id), fname, lname, row_person_opi_id)))
            else: 
                import_report.warning(';'.join((self.REPORT_PERSON_NEW_EXIST_DUPLICATES, str(person_id), fname, lname, row_person_opi_id)))
                import_report.warning(';'.join((self.REPORT_PERSON_DUPLICATE, str(person_duplicate_id))))
                logger.warning(self.LOG_MSG_DUPLICATE_OBJECT)
                logger.warning('Existing object: person_fist_name=' + fname + ' person_last_name=' + lname + ' person_id=' + str(person_id))
                logger.warning('Duplicate object: ' + ' person_id=' + str(person_duplicate_id))
        else:
            import_report.info(';'.join((self.REPORT_PERSON_NEW, str(person_id), fname, lname, row_person_opi_id)))
        return super(PersonResource, self).before_import_row(row, **kwargs)
    
    def before_save_instance(self, instance, using_transactions, dry_run):
        instance.is_imported = True
        return super(PersonResource, self).before_save_instance(instance, using_transactions, dry_run)
    
    def after_save_instance(self, instance, using_transactions, dry_run):
        if dry_run:
            return
        #current_institutions = instance.person_institutions.all()
        principal_affiliations = self.person_import_helper.get_principal_affiliation(instance.person_id)
        affiliations = self.person_import_helper.get_affiliations(instance.person_id)
        if self.institutions:
            if self.institutions[0].institution_id not in principal_affiliations:
                paff = PersonAffiliation()
                paff.person = instance
                paff.institution = self.institutions[0]
                paff.is_principal = True
                paff.save()
            for institution in self.institutions[1:]:
                if institution.institution_id not in affiliations:
                    paff = PersonAffiliation()
                    paff.person = instance
                    paff.institution = institution
                    paff.is_principal = False
                    paff.save()
            current_disciplines = self.person_import_helper.get_person_disciplines(instance.person_id)
            if self.disciplines:
                for discipline in self.disciplines:
                    if discipline not in current_disciplines:
                        instance.person_disciplines.add(discipline)
                instance.save()
        logger.info(self.LOG_MSG_ADDED_OBJECT + ("%d %s %s" % (instance.person_id, instance.person_first_name, instance.person_last_name)))
        import_report.info(';'.join((self.REPORT_PERSON_SAVED, str(instance.person_id), instance.person_first_name, instance.person_last_name, str(instance.person_opi_id))))          
        return super(PersonResource, self).after_save_instance(instance, using_transactions, dry_run)
           
    def import_data(self, dataset, dry_run=False, raise_errors=False, use_transactions=False, collect_failed_rows=False, **kwargs):
        if dry_run:
            logging.disable(logging.CRITICAL)
        else:
            logging.disable(logging.NOTSET)
        
        return super(PersonResource, self).import_data(dataset, dry_run, raise_errors, use_transactions, collect_failed_rows, **kwargs)

    
    class Meta:
        fields = ('person_opi_id', 'person_first_name', 'person_last_name', 'person_title', 'person_institutions', 'person_email', 'person_kbn', 'person_spec', 'person_foreigner', 'person_died')
        import_id_fields = ('person_id',)
        skip_unchanged = True
        report_skipped = True
        model = Person
