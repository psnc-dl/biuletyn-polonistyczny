  # -*- coding: utf-8 -*-
class FieldJobOfferDiscipline():
    VERBOSE_NAME = 'Dyscyplina oferty pracy'
    VERBOSE_NAME_PLURAL = 'Dyscypliny ofert pracy'
    NAME = 'Nazwa dyscypliny'

class FieldJobOfferType():
    VERBOSE_NAME = 'Forma pracy'
    VERBOSE_NAME_PLURAL = 'Formy pracy'
    TYPE_NAME = "Nazwa"

class FieldJobOffer():
    VERBOSE_NAME = 'Oferta pracy'
    VERBOSE_NAME_PLURAL = 'Oferty pracy'
    POSITION = 'Stanowisko'
    LEAD = 'Akapit wprowadzający'    
    DESCRIPTION = 'Opis'        
    IMAGE = 'Zdjęcie'
    IMAGE_COPYRIGHT = 'Prawa/licencja do zdjęcia'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    DISCIPLINES = 'Dziedziny'
    TYPE = 'Forma pracy'
    CITY = 'Miasto'
    REGION = 'Województwo'
    DOMAIN = 'Dziedzina'
    CITIES = 'Miasta'
    REGIONS = 'Województwa'
    DATE_START = 'Data ogłoszenia'
    DATE_END = 'Termin nadsyłania zgłoszeń'
    INSTITUTION = 'Instytucja'
    KEYWORDS = 'Słowa kluczowe'
    CONNECTED_PROJECTS = 'Powiązane projekty'     
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'
    ADDED_BY = 'Dodana przez'
    MODIFIED_BY = 'Modyfikowana przez'
    IS_PROMOTED = 'Oferta promowana'
    IS_ACCEPTED = 'Opublikuj'

class FieldJobOfferFile():
    VERBOSE_NAME = 'Oferta pracy plik'
    VERBOSE_NAME_PLURAL = 'Oferta pracy pliki'
    JOB_OFFER = 'Oferta pracy'
    FILE = "Plik"
    COPYRIGHT = 'Prawa autorskie/licencja'

class FieldJobOfferLink():
    VERBOSE_NAME = 'link powiązany z ofertą pracy'
    VERBOSE_NAME_PLURAL = 'linki powiązane z ofertami prac'
    JOB_OFFER = 'Oferta pracy'
    LINK = 'Link'

class FieldJobOfferContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    JOB_OFFER = 'Oferta pracy'
    PERSON = 'Osoba'
    ROLE = 'Rola'

class FieldJobOfferAuthorized():    
    VERBOSE_NAME = 'Uprawnienia instytucji do oferty'
    VERBOSE_NAME_PLURAL = 'Uprawnienia instytucji do ofert'
    AUTHORIZED = 'Uprawnienie'
    JOB_OFFER = 'Oferta pracy' 
    
class FieldJobOfferModification():
    VERBOSE_NAME = 'modyfikacja oferty pracy'
    VERBOSE_NAME_PLURAL = 'modyfikacje ofert pracy'
    JOB_OFFER = 'Oferta pracy' 
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldJobOfferFilter():
    STATUS = 'Status'
    ONLY_MY = 'Tylko moje oferty'
