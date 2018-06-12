# -*- coding: utf-8 -*-
class FieldCompetition():
    VERBOSE_NAME = 'Konkurs'
    VERBOSE_NAME_PLURAL = 'Konkursy'
    TITLE = 'Tytuł konkursu'
    LEAD = 'Akapit wprowadzający'
    DESCRIPTION = 'Opis konkursu'    
    IMAGE_COPYRIGHT = 'Prawa/licencja do obrazu'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    DEADLINE_DATE = 'Termin zgłaszania'
    TARGETS = 'Grupy docelowe'
    IMAGE = 'Obraz'
    CITY = 'Miasto'
    REGION = 'Województwo'
    INSTITUTION = 'Instytucja nadzorująca'
    INSTITUTIONS = 'Instytucje nadzorujące'
    KEYWORDS = 'Słowa kluczowe'
    CONNECTED_EVENTS = 'Powiązane wydarzenia'       
    CONNECTED_PROJECTS = 'Powiązane projekty'      
    ADDED_BY = 'Dodany przez'
    MODIFIED_BY = 'Zmodyfikowany przez'
    IS_ACCEPTED = 'Opublikuj'
    IS_PROMOTED = 'Konkurs promowany'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'

class FieldCompetitionFile():
    VERBOSE_NAME = 'plik dołączony do konkursu'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do konkursów'
    METADATA = 'Metadane pliku'
    COMPETITION = 'Konkurs'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'    
    
class FieldCompetitionLink():
    VERBOSE_NAME = 'link powiązany z konkursem'
    VERBOSE_NAME_PLURAL = 'linki powiązane z konkursami'
    COMPETITION = 'Konkurs'
    LINK = 'Link'
    
class FieldCompetitionContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    COMPETITION = 'Konkurs'
    PERSON = 'Osoba'
    ROLE = 'Rola'

class FieldCompetitionDestinantionGroup():
    STU_NAME = 'Studenci'
    ABS_NAME = 'Absolwenci'
    DOC_NAME = 'Doktoranci'
    SCI_NAME = 'Kadra naukowa'
    
class FieldCompetitionAuthorized():    
    VERBOSE_NAME = 'uprawnienia instytucji do konkursu'
    VERBOSE_NAME_PLURAL = 'uprawnienia instytucji do konkursów'
    AUTHORIZED = 'Uprawnienie'
    COMPETITION = 'Konkurs' 
    
class FieldCompetitionModification():
    VERBOSE_NAME = 'modyfikacja konkursu'
    VERBOSE_NAME_PLURAL = 'modyfikacje konkursów'
    COMPETITION = 'Konkurs'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldCompetitionFilter():
    STATUS = 'Status'
    ONLY_MY = 'Tylko moje konkursy'
    