from django import forms


class SearchForm(forms.Form):
    search_name = forms.CharField(required=False)

    def as_p(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(
            normal_row=u'<tr><td><input type="text" class="form-control" name="search_name" '
                       u'placeholder="NOME COMPLETO" id="id_search_name" required /></td>',
            error_row=u'%s',
            row_ender='</tr>',
            help_text_html=u' <span class="helptext">%s</span>',
            errors_on_separate_row=True)


class NameListForm(forms.Form):
    group_checkboxes = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
    )
    delete_checkboxes = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
    )


class IndexForm(forms.Form):
    pass
