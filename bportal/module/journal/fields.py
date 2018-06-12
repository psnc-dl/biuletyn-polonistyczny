# -*- coding: utf-8 -*-
class FieldJournal():
    VERBOSE_NAME = 'Czasopismo'
    VERBOSE_NAME_PLURAL = 'Czasopisma'
    TITLE = 'Tytuł'
    LEAD = 'Akapit wprowadzający'
    PUBLISHER = 'Wydawca'
    CATEGORY = 'Kategoria'  
    CATEGORIES = 'Kategorie'
    EDITORIAL_OFFICE = 'Adres redakcji'
    EDITOR_IN_CHIEF = 'Redaktor naczelny'
    FIRST_ISSUE_DATE = 'Data pierwszego numeru'
    KEYWORDS = 'Słowa kluczowe'
    ADDED_BY = 'Dodany przez'    
    MODIFIED_BY = 'Zmodyfikowany przez'
    IS_ACCEPTED = 'Opublikuj'    
    IS_PROMOTED = 'Czasopismo promowane'

class FieldJournalIssue():
    VERBOSE_NAME = 'Numer czasopisma'
    VERBOSE_NAME_PLURAL = 'Numery czasopism'
    TITLE = 'Tytuł numeru'
    LEAD = 'Akapit wprowadzający'
    DESCRIPTION = 'Opis numeru'
    CATEGORY = 'Kategoria'
    CATEGORIES = 'Kategorie'
    TABLE_OF_CONTENTS = 'Spis treści'
    JOURNAL = 'Czasopismo'   
    IMAGE_COPYRIGHT = 'Prawa/licencja do obrazu'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    PUBLICATION_DATE = 'Data publikacji'
    IMAGE = 'Obraz'
    ISSN = 'ISSN'
    VOLUME = 'Tom'
    NUMBER = 'Numer'
    YEAR = 'Rok'
    PUBLISHER = 'Wydawca'
    PUBLISHERS = 'Wydawcy'
    PAGES = 'Strony'
    KEYWORDS = 'Słowa kluczowe'
    ADDED_BY = 'Dodany przez'
    MODIFIED_BY = 'Zmodyfikowany przez'
    IS_ACCEPTED = 'Opublikuj'
    IS_PROMOTED = 'Numer czasopisma promowany'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'

class FieldJournalIssueFile():
    VERBOSE_NAME = 'plik dołączony do numeru czasopisma'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do numerów czasopism'
    METADATA = 'Metadane pliku'
    JOURNALISSUE = 'Numer czasopisma'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'    
    
class FieldJournalIssueLink():
    VERBOSE_NAME = 'link powiązany z numerem czasopisma'
    VERBOSE_NAME_PLURAL = 'linki powiązane z numerami czasopism'
    JOURNALISSUE = 'Numer czasopisma'
    LINK = 'Link'
    
class FieldJournalIssueContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    JOURNALISSUE = 'Numer czasopisma'
    PERSON = 'Osoba'
    ROLE = 'Rola'
   
class FieldJournalIssueAuthorized():    
    VERBOSE_NAME = 'uprawnienia instytucji do numeru czasopisma'
    VERBOSE_NAME_PLURAL = 'uprawnienia instytucji do noumerów czasopism'
    AUTHORIZED = 'Uprawnienie'
    JOURNALISSUE = 'Numer czasopisma'
    
class FieldJournalIssueModification():
    VERBOSE_NAME = 'modyfikacja numeru czasopisma'
    VERBOSE_NAME_PLURAL = 'modyfikacje numerów czasopism'
    JOURNALISSUE = 'Numer czasopisma'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldJournalIssueFilter():
    ONLY_MY = 'Tylko moje numery czasopism'
    