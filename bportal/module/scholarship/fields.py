  # -*- coding: utf-8 -*-
class FieldScholarshipType():
    VERBOSE_NAME = 'Typ stypendium'
    VERBOSE_NAME_PLURAL = 'Typy stypendiów'
    TYPE_SHORT = 'Skrót'
    TYPE_NAME = "Nazwa"

class FieldScholarship():
    VERBOSE_NAME = 'Stypednium'
    VERBOSE_NAME_PLURAL = 'Stypendia'
    NAME = 'Nazwa stypendium'
    LEAD = 'Akapit wprowadzający'
    DESCRIPTION = 'Opis'        
    IMAGE = 'Zdjęcie'
    IMAGE_COPYRIGHT = 'Prawa/licencja do zdjęcia'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    FOUNDER = 'Fundator/organizator'
    DATE_START = 'Data ogłoszenia'
    DATE_END = 'Termin nadsyłania zgłoszeń'
    CITY = 'Miasto'
    REGION = 'Województwo'
    KEYWORDS = 'Słowa kluczowe'
    CONNECTED_PROJECTS = 'Powiązane projekty'     
    TARGETS = 'Grupa docelowa'
    ADDED_BY = 'Dodane przez'
    MODIFIED_BY = 'Zmodyfikowane przez'
    TYPE = 'Typ'
    IS_PROMOTED = 'Stypendium promowane'
    IS_ACCEPTED = 'Opublikuj'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'    

class FieldScholarshipFile():
    VERBOSE_NAME = 'Stypendium załącznik'
    VERBOSE_NAME_PLURAL = 'Stypendium załączniki'
    SCHOLARSHIP = 'Stypendium'
    FILE = "Plik"
    COPYRIGHT = 'Prawa autorskie/licencja'

class FieldScholarshipLink():
    VERBOSE_NAME = 'link powiązany ze stypendium'
    VERBOSE_NAME_PLURAL = 'linki powiązane ze stypendiami'
    SCHOLARSHIP = 'Stypendium'
    LINK = 'Link'
    
class FieldScholarshipContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    SCHOLARSHIP = 'Stypendium'
    PERSON = 'Osoba'
    ROLE = 'Rola'

class FieldScholarshipAuthorized():    
    VERBOSE_NAME = 'Uprawnienia instytucji do stypednium'
    VERBOSE_NAME_PLURAL = 'Uprawnienia instytucji do stypendium'
    AUTHORIZED = 'Uprawnienie'
    SCHOLARSHIP = 'Stypendium'
    
class FieldScholarshipModification():
    VERBOSE_NAME = 'modyfikacja stypendium'
    VERBOSE_NAME_PLURAL = 'modyfikacje stypendiów'
    SCHOLARSHIP = 'Stypendium'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'    

class FieldScholarshipFilter():
    STATUS = 'Status'
    ONLY_MY = 'Tylko moje stypendia'
    