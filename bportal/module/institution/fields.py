# -*- coding: utf-8 -*-
class FieldInstitutionType():
    VERBOSE_NAME = 'Typ instytucji'
    VERBOSE_NAME_PLURAL = 'Typy instytucji'
    NAME = 'Nazwa typu'

class FieldInstitution():
    VERBOSE_NAME = 'Instytucja'
    VERBOSE_NAME_PLURAL = 'Instytucje'
    SHORTNAME = 'Skrót'
    FULLNAME = 'Nazwa'
    TYPE = 'Typ'
    CITY = 'Miasto'
    PARENT = 'Instytucja macierzysta'
    PHOTO = 'Zdjęcie'
    WWW = 'Witryna'
    DESCRIPTION = 'Opis instytucji'    
    
class FieldInstitutionRole():
    VERBOSE_NAME = 'rola instytucji'
    VERBOSE_NAME_PLURAL = 'role instytucji'
    ROLE = 'Rola'
