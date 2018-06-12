# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand
import logging
from tablib.core import Dataset

from bportal.module.person.resources import PersonResource


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'IMPORT PEOPLE FROM CSV FILE'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            help='import selected csv file',
        )
               
    def peopleImport(self, fname):
        start = datetime.datetime.now()
        
        imported_data = Dataset().load(open(fname).read())
        person_resource = PersonResource()
        result = person_resource.import_data(imported_data, dry_run=False)
        
        if result.has_errors():
            logger.info('IMPORT COMPLETED WITH ERRORS: ')
            logger.info(result)
            print(result)
            return
        else:
            end = datetime.datetime.now()
            delta = end - start
            logger.info('IMPORT SUCCESSFULLY COMPLETED IN TIME: ' + str(delta))   
                    
    def handle(self, *args, **options):
        logger.info('--- IMPORT PEOPLE DATA ---')
        logger.info('-------------------------')
        logger.info('Import started...')
        logger.info(' ')
        if options['file']:
            self.peopleImport(options['file'])
        logger.info(' done.')
        logger.info(' ')
        logger.info('-------------------------')
        logger.info('---- - END OF IMPORT ----')