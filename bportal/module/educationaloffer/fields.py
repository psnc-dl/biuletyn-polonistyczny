  # -*- coding: utf-8 -*-
class FieldEducationalOfferType():
    VERBOSE_NAME = 'Typ oferty edukacyjnej'
    VERBOSE_NAME_PLURAL = 'Typy ofert edukacyjnych'
    TYPE_SHORT = 'Skrót'
    TYPE_NAME = "Nazwa"

class FieldEducationalOfferMode():
    VERBOSE_NAME = 'Tryb oferty edukacyjnej'
    VERBOSE_NAME_PLURAL = 'Tryby ofert edukacyjnych'
    MODE_SHORT = 'Skrót'
    MODE_NAME = "Nazwa"
        
class FieldEducationalOffer():
    VERBOSE_NAME = 'Oferta edukacyjna'
    VERBOSE_NAME_PLURAL = 'Oferty edukacyjne'
    POSITION = 'Nazwa studiów'
    LEAD = 'Akapit wprowadzający'    
    DESCRIPTION = 'Opis'        
    IMAGE = 'Zdjęcie'
    IMAGE_COPYRIGHT = 'Prawa/licencja do zdjęcia'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    TUITION = 'Wysokość czesnego'
    PERIOD = 'Długość trwania kursu'
    TYPE = 'Rodzaj oferty'
    MODE = 'Tryb'
    CITY = 'Miasto'
    REGION = 'Województwo'
    DATE_START = 'Data ogłoszenia'
    DATE_END = 'Termin nadsyłania zgłoszeń'
    INSTITUTION = 'Instytucja'
    KEYWORDS = 'Słowa kluczowe'
    CONNECTED_PROJECTS = 'Powiązane projekty'      
    ADDED_BY = 'Dodana przez'
    MODIFIED_BY = 'Modyfikowana przez'
    IS_PROMOTED = 'Oferta edukacyjna promowana'
    IS_ACCEPTED = 'Opublikuj'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'

class FieldEducationalOfferFile():
    VERBOSE_NAME = 'Oferta edukacyjna plik'
    VERBOSE_NAME_PLURAL = 'Oferta edukacyjna pliki'
    EDUCATIONAL_OFFER = 'Oferta edukacyjna'
    FILE = "Plik"
    COPYRIGHT = 'Prawa autorskie/licencja'
    
class FieldEducationalOfferLink():
    VERBOSE_NAME = 'link powiązany z ofertą edukacyjną'
    VERBOSE_NAME_PLURAL = 'linki powiązane z ofertami edukacyjnymi'
    EDUCATIONAL_OFFER = 'Oferta edukacyjna'
    LINK = 'Link'
        
class FieldEducationalOfferContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    EDUCATIONAL_OFFER = 'Oferta edukacyjna'
    PERSON = 'Osoba'
    ROLE = 'Rola'

class FieldEducationalOfferAuthorized():    
    VERBOSE_NAME = 'Uprawnienia instytucji do oferty'
    VERBOSE_NAME_PLURAL = 'Uprawnienia instytucji do ofert'
    AUTHORIZED = 'Uprawnienie'
    EDUCATIONAL_OFFER = 'Oferta edukacyjna' 
    
class FieldEducationalOfferModification():
    VERBOSE_NAME = 'modyfikacja oferty edukacyjnej'
    VERBOSE_NAME_PLURAL = 'modyfikacje ofert edukacyjnych'
    EDUCATIONAL_OFFER = 'Oferta edukacyjna' 
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldEducationalOfferFilter():
    STATUS = 'Status'
    ONLY_MY = 'Tylko moje oferty'
    