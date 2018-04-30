"""
Admin customisations to allow exporting of selected objects as CSV.
"""

import uuid, csv

from django.contrib import admin
from django.conf.urls import url
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text


def export_selected_objects(modeladmin, request, queryset):
    """
    Admin action to allow the export of the selected objects.
    """
    base_url = reverse('admin:{}_{}_export'.format(
        queryset.model._meta.app_label, queryset.model._meta.model_name
    ))
    selected_ids = queryset.values_list('pk', flat = True)
    return redirect(
        base_url + "?ids={}".format(",".join(str(pk) for pk in selected_ids))
    )
export_selected_objects.short_description = 'Export selected objects'
# Add as a default action for all modeladmins
admin.site.add_action(export_selected_objects, 'export_selected_objects')


class RawIdWidget(forms.TextInput):
    """
    Widget to allow selecting of raw model IDs. Mostly stolen from the admin.
    """
    def __init__(self, model, admin_site, attrs = None):
        self.model = model
        self.admin_site = admin_site
        super().__init__(attrs)

    def render(self, name, value, attrs = None):
        if attrs is None:
            attrs = {}
        if value:
            value = ','.join(force_text(v) for v in value)
        else:
            value = ''
        extra = []
        if self.model in self.admin_site._registry:
            # The related object is registered with the same AdminSite
            attrs['class'] = 'vManyToManyRawIdAdminField'
            # The related object is registered with the same AdminSite
            related_url = reverse(
                'admin:{}_{}_changelist'.format(
                    self.model._meta.app_label,
                    self.model._meta.model_name,
                ),
                current_app = self.admin_site.name,
            )
            extra.append(
                '<a href="%s" class="related-lookup" id="lookup_id_%s" title="Lookup"></a>'
                % (related_url, name)
            )
        output = [super().render(name, value, attrs)] + extra
        if value:
            output.append(self.label_for_value(value))
        return mark_safe(''.join(output))

    def label_for_value(self, value):
        return ''

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            return value.split(',')


def allowed_fields_for_export(model):
    # Only allow concrete, non-relation fields to be exported
    return [
        f.name
        for f in model._meta.get_fields()
        if f.concrete and (not f.is_relation or
                           f.one_to_one or
                           (f.many_to_one and f.related_model))
    ]

def get_export_form(model, admin_site):
    """
    Build an export form for the given model.
    """
    return type(uuid.uuid4().hex, (forms.Form, ), {
        'objects' : forms.ModelMultipleChoiceField(
            queryset = model.objects.all(),
            widget = RawIdWidget(model, admin_site),
            help_text = 'The ids of the objects to export'
        ),
        'fields' : forms.MultipleChoiceField(
            choices = [(f, f) for f in allowed_fields_for_export(model)],
            widget = forms.SelectMultiple(attrs = { 'class' : 'use-select2' }),
            help_text = 'The fields to export'
        )
    })

# Monkey-patch ModelAdmin with methods for export
def export_objects(self, request):
    """
    View for exporting objects.
    """
    # We only allow concrete, non-relation fields to be exported
    export_form = get_export_form(self.model, self.admin_site)
    if request.method == 'POST':
        form = export_form(request.POST)
        if form.is_valid():
            # Export the selected data as CSV
            response = HttpResponse(content_type='text/plain')
            selected_fields = form.cleaned_data['fields']
            writer = csv.DictWriter(response, fieldnames = selected_fields)
            # Only write the header if we have more than one field
            if len(selected_fields) > 1:
                writer.writeheader()
            for obj in form.cleaned_data['objects']:
                writer.writerow({ k : getattr(obj, k) for k in selected_fields })
            return response
    else:
        form = export_form(initial = {
            'fields' : allowed_fields_for_export(self.model),
            'objects' : request.GET.get('ids', '').split(',')
        })
    return render(request, 'admin/export/export_form.html', {
        'title' : 'Export {}'.format(self.model._meta.verbose_name_plural),
        'form' : form,
        'media' : self.media + form.media,
        'opts' : self.model._meta,
        'form_url' : reverse('admin:{}_{}_export'.format(
            self.model._meta.app_label, self.model._meta.model_name
        ))
    })
admin.ModelAdmin.export_objects = export_objects

def patch_get_urls(parent):
    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            url(r'^export/$',
                self.admin_site.admin_view(self.export_objects),
                name = '{}_{}_export'.format(*info)),
        ] + parent(self)
    return get_urls
admin.ModelAdmin.get_urls = patch_get_urls(admin.ModelAdmin.get_urls)
