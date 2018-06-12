# -*- coding: utf-8 -*-
import locale
import logging

from django.core.files.storage import FileSystemStorage
from django.utils import encoding
from import_export.tmp_storages import MediaStorage


logger = logging.getLogger(__name__)


class UtfFileSystemStorage(FileSystemStorage):
    
    """
    Convert ASCII characters in name to unicode characters.
    """
    def get_valid_name(self, name):
        logger.debug('getting valid name for the file: ' + name)
        name = encoding.smart_str(name, encoding='utf-8', errors='ignore')
        logger.debug('got valid name for the file: ' + name)
        return super(UtfFileSystemStorage, self).get_valid_name(name)



class UtfImportExportStorage(MediaStorage):

    def read(self, read_mode='rb'):
        logger.debug('locale: ' + locale.getpreferredencoding(False))
        return super(UtfImportExportStorage, self).read(read_mode)

