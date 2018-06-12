# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand
import logging
from tablib.core import Dataset

from bportal.module.project.resources import ProjectResource


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'IMPORT PROJECTS FROM CSV FILE'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            help='import selected csv file',
        )
               
    def projectsImport(self, fname):
        start = datetime.datetime.now()
        
        imported_data = Dataset().load(open(fname).read())
        project_resource = ProjectResource()
        result = project_resource.import_data(imported_data, dry_run=False)
        
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
        logger.info('--- IMPORT PROJECT DATA ---')
        logger.info('-------------------------')
        logger.info('Import started...')
        logger.info(' ')
        if options['file']:
            self.projectsImport(options['file'])
        logger.info(' done.')
        logger.info(' ')
        logger.info('-------------------------')
        logger.info('---- - END OF IMPORT ----')