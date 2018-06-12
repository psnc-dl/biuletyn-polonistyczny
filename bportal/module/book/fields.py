# -*- coding: utf-8 -*-
class FieldBook():
    VERBOSE_NAME = 'Nowość wydawnicza'
    VERBOSE_NAME_PLURAL = 'Nowości wydawnicze'
    TITLE = 'Tytuł nowości wydawniczej'
    LEAD = 'Akapit wprowadzający'
    DESCRIPTION = 'Opis nowości wydawniczej'
    TABLE_OF_CONTENTS = 'Spis treści'     
    IMAGE_COPYRIGHT = 'Prawa/licencja do obrazu'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    CATEGORY = 'Kategoria'
    CATEGORIES = 'Kategorie'
    PUBLICATION_DATE = 'Data publikacji'
    IMAGE = 'Obraz'
    AUTHORS = 'Autorzy/Redaktorzy'
    ISBN = 'ISBN'
    PUBLISHER = 'Wydawca'
    PUBLISHERS = 'Wydawcy'
    PAGES = 'Strony'
    KEYWORDS = 'Słowa kluczowe'
    ADDED_BY = 'Dodany przez'
    MODIFIED_BY = 'Zmodyfikowany przez'
    IS_ACCEPTED = 'Opublikuj'
    IS_PROMOTED = 'Nowość wydawnicza promowana'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'

class FieldBookFile():
    VERBOSE_NAME = 'plik dołączony do nowości wydawniczej'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do nowości wydawniczych'
    METADATA = 'Metadane pliku'
    BOOK = 'Nowość wydawnicza'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'    
    
class FieldBookLink():
    VERBOSE_NAME = 'link powiązany z nowością wydawniczą'
    VERBOSE_NAME_PLURAL = 'linki powiązane z nowościami wydawniczymi'
    BOOK = 'Nowość wydawnicza'
    LINK = 'Link'
    
class FieldBookContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    BOOK = 'Nowość wydawnicza'
    PERSON = 'Osoba'
    ROLE = 'Rola'
   
class FieldBookAuthorized():    
    VERBOSE_NAME = 'uprawnienia instytucji do nowości wydawniczej'
    VERBOSE_NAME_PLURAL = 'uprawnienia instytucji do nowości wydawniczych'
    AUTHORIZED = 'Uprawnienie'
    BOOK = 'Nowość wydawnicza'
    
class FieldBookModification():
    VERBOSE_NAME = 'modyfikacja nowości wydawniczej'
    VERBOSE_NAME_PLURAL = 'modyfikacje nowości wydawniczych'
    BOOK = 'Nowość wydawnicza'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldBookFilter():
    ONLY_MY = 'Tylko moje nowości wydawnicze'
    