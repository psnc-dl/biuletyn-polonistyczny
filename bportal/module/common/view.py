# -*- coding: utf-8 -*-
import logging
import mimetypes
import os
import re
import stat


from django.http import Http404, FileResponse, HttpResponse
from django.utils._os import safe_join
from django.utils.encoding import force_text
from django.utils.http import http_date
from django.utils.text import get_text_list
from django.utils.translation import ugettext as _
from django.views.generic.base import View

from bportal.settings import MEDIA_ROOT


logger = logging.getLogger(__name__)

class ChangeMessageView(object):
    
    def construct_change_message(self, form, formsets, add=False):
        change_message = []
        if add:
            change_message.append(_('Added.'))
        elif form.changed_data:
            change_message.append(_('Changed %s.') % get_text_list(form.changed_data, _('and')))

        if formsets:
            for formset in formsets:
                for added_object in formset.new_objects:
                    change_message.append(_('Added %(name)s "%(object)s".')
                                          % {'name': force_text(added_object._meta.verbose_name),
                                             'object': force_text(added_object)})
                for changed_object, changed_fields in formset.changed_objects:
                    change_message.append(_('Changed %(list)s for %(name)s "%(object)s".')
                                          % {'list': get_text_list(changed_fields, _('and')),
                                             'name': force_text(changed_object._meta.verbose_name),
                                             'object': force_text(changed_object)})
                for deleted_object in formset.deleted_objects:
                    change_message.append(_('Deleted %(name)s "%(object)s".')
                                          % {'name': force_text(deleted_object._meta.verbose_name),
                                             'object': force_text(deleted_object)})
        change_message = ' '.join(change_message)
        return change_message or _('No fields changed.')


class DownloadView(View):
    
    def get(self, request):
        location = request.GET.get('location')
        fullpath = safe_join(MEDIA_ROOT, location)
        if not os.path.exists(fullpath):
            raise Http404(_('"%(path)s" does not exist') % {'path': fullpath})
        statobj = os.stat(fullpath)
        content_type, encoding = mimetypes.guess_type(fullpath)
        content_type = content_type or 'application/octet-stream'
        response = FileResponse(open(fullpath, 'rb'), content_type=content_type)
        response["Last-Modified"] = http_date(statobj.st_mtime)
        if stat.S_ISREG(statobj.st_mode):
            response["Content-Length"] = statobj.st_size
        if encoding:
            response["Content-Encoding"] = encoding
        response['Content-Disposition'] = 'attachment; filename="%s"' % location.split('/')[-1]
        return response
    

class TestView(View):
    
    def get(self, request):
        regex = re.compile('^HTTP_')
        headers = dict()
        for (header, value) in request.META.items():
            if header.startswith('HTTP_'):
                headers[regex.sub('', header)] = value 
        
        result = '<br/><br/>'.join('{}: {}'.format(k.lower().title().replace('_', '-'), v) for k, v in headers.items())
        html = "<html><body>"
        html = html + "absulute_uri:<br/><br/>"
        html = html + request.build_absolute_uri('')
        html = html + "<br/><br/>headers:<br/><br/>"
        html = html + result
        html = html + "</body></html>"        
        return HttpResponse(html)

