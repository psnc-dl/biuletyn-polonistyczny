# -*- coding: utf-8 -*-
import logging
import weasyprint
from django.http.response import HttpResponse
from django.utils import translation
from django.template.loader import get_template
from django.template.context import Context
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

def __generateHtmlContent(context, template_name):
    translation.activate('pl')
    template = get_template(template_name)
    return template.render(Context(context))
    

def generatePdfFile(context, template_name):
    try:
        html = __generateHtmlContent(context, template_name)    
        pdf = weasyprint.HTML(string=html).write_pdf()
        return ContentFile(content=pdf)
    except Exception as e:
        logger.error(e)
        pass

    
def generateHttpResponse(request, context, template_name):
    response = HttpResponse(content_type="application/pdf")
    try:
        html = __generateHtmlContent(context, template_name)
        weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)
    except Exception as e:
        logger.error(e)
        pass
        
    return response