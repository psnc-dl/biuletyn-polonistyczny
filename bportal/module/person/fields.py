# -*- coding: utf-8 -*-
class FieldPerson():
    VERBOSE_NAME = 'Osoba'
    VERBOSE_NAME_PLURAL = 'Osoby'
    FIRTS_NAME = 'Imię'
    LAST_NAME = 'Nazwisko'
    TITLE = 'Tytuł naukowy'
    INSTITUTIONS = 'Afiliacje'
    OPI_ID = 'OPI ID'
    EMAIL = 'Email'
    PHOTO = 'Zdjęcie'
    BIOGRAM = 'Biogram'
    DISCIPLINES = 'Dyscypliny'

class FieldScientificTitle(): 
    VERBOSE_NAME = 'tytuł naukowy'
    VERBOSE_NAME_PLURAL = 'tytuły naukowe'
    ABBREVIATION = 'Skrót'
    NAME = 'Tytuł'
    
class FieldPersonAffiliation():
    VERBOSE_NAME = 'afiliacja'
    VERBOSE_NAME_PLURAL = 'afiliacje'
    PERSON = 'Osoba'
    INSTITUTION = 'Instytucja'
    IS_PRINCIPAL = 'Podstawowa'

class FieldPersonContributionRole():
    VERBOSE_NAME = 'rodzaj wkładu osoby'
    VERBOSE_NAME_PLURAL = 'rodzaje wkładu osób'
    ROLE = 'Rola'
