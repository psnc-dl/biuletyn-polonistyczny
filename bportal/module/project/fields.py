# -*- coding: utf-8 -*-
class FieldProject():
    VERBOSE_NAME = 'Projekt'
    VERBOSE_NAME_PLURAL = 'Projekty'
    TITLE = 'Tytuł'
    LEAD = 'Akapit wprowadzający'    
    DESCRIPTION = 'Opis projektu'
    INSTITUTION = 'Instytucja'    
    INSTITUTIONS = 'Instytucje'
    DATE_START = 'Data rozpoczęcia'
    DATE_END = 'Data zakończenia' 
    DISCIPLINES = 'Dyscypliny'
    CITY = 'Miasto'
    CITIES = 'Miasta'
    REGION = 'Region'
    REGIONS = 'Regiony'
    TARGETS = 'Grupy docelowe'
    FINANCING = 'Finansowanie'
    PARTICIPANTS = 'Uczestnicy'
    IMAGE = 'Obraz'
    IMAGE_COPYRIGHT = 'Prawa/licencja do obrazu'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    CONTACT = 'Kontakt'
    SUPPORT = 'Możliwość współpracy'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'
    CONNECTED_EVENTS = 'Powiązane wydarzenia'
    CONNECTED_DISSERTATIONS = 'Powiązane rozprawy'
    CONNECTED_COMPETITIONS = 'Powiązane konkursy'
    CONNECTED_JOBOFFERS = 'Powiązane oferty pracy'
    CONNECTED_EDUOFFERS = 'Powiązane oferty edukacyjne'
    CONNECTED_SCHOLARSHIPS  = 'Powiązane stypendia' 
    KEYWORDS = 'Słowa kluczowe'
    ADDED_BY = 'Dodany przez'    
    MODIFIED_BY = 'Zmodyfikowany przez'
    IS_ACCEPTED = 'Opublikuj'
    IS_PROMOTED = 'Projekt promowany'
    OPI_ID = 'OPI ID'

class FieldProjectParticipant():
    VERBOSE_NAME = 'rola uczestnika w projekcie'
    VERBOSE_NAME_PLURAL = 'role uczestników w projektach'
    PERSON = 'Uczestnik'
    PROJECT = 'Projekt'
    IS_PRINCIPAL = 'Kierownik'

class FieldProjectInstitution():
    VERBOSE_NAME = 'rola instytucji w projekcie'
    VERBOSE_NAME_PLURAL = 'role instytucji w projektach'
    INSTITUTION = 'Instytucja'
    PROJECT = 'Projekt'
    ROLE = 'Rola'
    
class FieldProjectFile():
    VERBOSE_NAME = 'plik dołączony do projektu'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do projektów'
    METADATA = 'Metadane pliku'
    PROJECT = 'Projekt'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'
    
class FieldProjectLink():
    VERBOSE_NAME = 'link powiązany z projektem'
    VERBOSE_NAME_PLURAL = 'linki powiązane z projektem'
    PROJECT = 'Projekt'
    LINK = 'Link'

class FieldProjectContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    PROJECT = 'Projekt'
    PERSON = 'Osoba'
    ROLE = 'Rola'

class FieldProjectAuthorized():    
    VERBOSE_NAME = 'uprawnienia instytucji do projektu'
    VERBOSE_NAME_PLURAL = 'uprawnienia instytucji do projektów'
    AUTHORIZED = 'Uprawnienie'
    PROJECT = 'Projekt'  

class FieldProjectModification():
    VERBOSE_NAME = 'modyfikacja projektu'
    VERBOSE_NAME_PLURAL = 'modyfikacje projektu'
    PROJECT = 'Projekt'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldProjectFilter():
    STATUS = 'Status'
    ONLY_MY = 'Tylko moje projekty'

