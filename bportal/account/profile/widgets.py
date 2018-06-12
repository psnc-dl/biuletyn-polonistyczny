# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from django.forms.widgets import ClearableFileInput 


class UserPhotoWidget(widgets.ClearableFileInput):
    initial_text = ugettext_lazy('Currently')
    input_text = ugettext_lazy('Change')
    clear_checkbox_label = ugettext_lazy('Clear')

    template_with_initial = '%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'

    url_markup_template = '<a href="{0}">{1}</a>'

    def clear_checkbox_name(self, name):
        return name + '-clear'

    def clear_checkbox_id(self, name):
        return name + '_id'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        tmp = '<div class="customfile">'
        tmp += '<div class="customfile__box">'
        tmp += '<div class="customfile__box--input">'
        tmp += '<input type="text" readonly="" class="customfile__input">'
        tmp += '</div>'
        tmp += '<div class="customfile__box--button">'
        tmp += '<label for="id_photo" class="customfile__button">Przeglądaj…</label>'
        tmp += super(ClearableFileInput, self).render(name, value, attrs)
        tmp += '</div>'
        tmp += '</div>'
        tmp += '</div>'
        substitutions['input'] = tmp

        return mark_safe(template % substitutions)