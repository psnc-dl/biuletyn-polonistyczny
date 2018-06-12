# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from django.forms.widgets import ClearableFileInput, CheckboxInput
from django.utils.html import format_html, conditional_escape
from django.utils.encoding import force_text


class FileWidget(widgets.ClearableFileInput):
    initial_text = ugettext_lazy('Currently')
    input_text = ugettext_lazy('Change')
    clear_checkbox_label = ugettext_lazy('Clear')

    template_with_initial = '%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'

    template_with_clear = '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    url_markup_template = '<a href="{0}">{1}</a>'

    def clear_checkbox_name(self, name):
        """
        Given the name of the file input, return the name of the clear checkbox
        input.
        """
        return name + '-clear'

    def clear_checkbox_id(self, name):
        """
        Given the name of the clear checkbox input, return the HTML id for it.
        """
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
        tmp += '<label for="id_'
        tmp += name
        tmp += '" class="customfile__button">Przeglądaj…</label>'
        tmp += super(ClearableFileInput, self).render(name, value, attrs)
        tmp += '</div>'
        tmp += '</div>'
        tmp += '</div>'

        substitutions['input'] = tmp

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html(self.url_markup_template,
                                                   value.url,
                                                   force_text(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

        