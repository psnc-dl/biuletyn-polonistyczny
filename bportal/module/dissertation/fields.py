# -*- coding: utf-8 -*-
class FieldDissertation():
    VERBOSE_NAME = 'Rozprawa doktorska / habilitacyjna'
    VERBOSE_NAME_PLURAL = 'Rozprawy doktorskie i habilitacyjne'
    TITLE = 'Tytuł pracy'
    LEAD = 'Akapit wprowadzający'    
    DESCRIPTION = 'Streszczenie (krótki opis)'    
    AUTHOR = 'Autor'
    INSTITUTION = 'Uczelnia / Instytucja realizująca'
    DATE_START = 'Data otwarcia przewodu'
    DATE_END = 'Data zakończenia pracy'
    IMAGE = 'Obraz'
    CITY = 'Miasto'
    REGION = 'Województwo'
    IMAGE_COPYRIGHT = 'Prawa/licencja do obrazu'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    SUPERVISORS = 'Promotorzy'
    REVIEWERS = 'Recenzenci'
    DISCIPLINE = 'Dyscyplina'
    DISCIPLINES = 'Dyscypliny'
    FILE = 'Plik pracy (pdf)'
    TYPE = 'Rodzaj pracy'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'
    KEYWORDS = 'Słowa kluczowe'
    CONNECTED_EVENTS = 'Powiązane wydarzenia'    
    CONNECTED_PROJECTS = 'Powiązane projekty'    
    ADDED_BY = 'Dodany przez'
    MODIFIED_BY = 'Zmodyfikowany przez'
    IS_ACCEPTED = 'Opublikuj'
    IS_PROMOTED = 'Rozprawa promowana'
    AUTHORIZED = 'Uprawnienie'
    OPI_ID = 'OPI ID'
 
class FieldDissertationType():
    DOC_NAME = 'Rozprawa doktorska'
    HAB_NAME = 'Rozprawa habilitacyjna'

class FieldDissertationFile():
    VERBOSE_NAME = 'plik dołączony do pracy'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do prac'
    METADATA = 'Metadane pliku'
    DISSERTATION = 'Rozprawa doktorska / habilitacyjna'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'    

class FieldDissertationLink():
    VERBOSE_NAME = 'link powiązany z pracą'
    VERBOSE_NAME_PLURAL = 'linki powiązane z pracą'
    DISSERTATION = 'Rozprawa doktorska/habilitacyjna'
    LINK = 'Link'
        
class FieldDissertationContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    DISSERTATION = 'Rozprawa doktorska/habilitacyjna'
    PERSON = 'Osoba'
    ROLE = 'Rola'
    
class FieldDissertationAuthorized():    
    VERBOSE_NAME = 'uprawnienia instytucji do rozprawy'
    VERBOSE_NAME_PLURAL = 'uprawnienia instytucji do rozpraw'
    AUTHORIZED = 'Uprawnienie'
    DISSERTATION = 'Praca doktorska / habilitacyjna'
    
class FieldDissertationModification():
    VERBOSE_NAME = 'modyfikacja rozprawy'
    VERBOSE_NAME_PLURAL = 'modyfikacje rozpraw'
    DISSERTATION = 'Rozprawa'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldDissertationFilter():
    STATUS = 'Status'
    ONLY_MY = 'Tylko moje rozprawy'
    