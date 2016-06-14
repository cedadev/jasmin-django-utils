"""
Main module for the JASMIN enumfield library.

Provides a model field and associated form fields for use with a Python enum.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django import forms
from django.db import models
from django.utils.encoding import force_text
from django.db.models.fields import BLANK_CHOICE_DASH


class EnumChoiceFieldMixin(object):
    def prepare_value(self, value):
        # Widgets expect to get strings as values
        if value is None:
            return ''
        if hasattr(value, "value"):
            value = value.value
        return force_text(value)

    def valid_value(self, value):
        if hasattr(value, "value"):
            if super().valid_value(value.value):
                return True
        return super().valid_value(value)

class EnumChoiceField(EnumChoiceFieldMixin, forms.TypedChoiceField):
    pass

class EnumMultipleChoiceField(EnumChoiceFieldMixin, forms.TypedMultipleChoiceField):
    pass


class EnumField(models.CharField):
    """
    Custom model field that allows selection from an enum.
    """
    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        # Set max_length to the maximum size of the enum values
        kwargs['max_length'] = max(len(e.value) for e in enum)
        # Set the choices to the enum choices
        kwargs['choices'] = [(e, e.name) for e in enum]
        super().__init__(*args, **kwargs)
        # Clear any validators - the only validation we need is blank/null and
        # membership of the enum
        self.validators = []

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Insert the enum at the start of args
        args = [self.enum] + list(args)
        # We supply max_length and choices
        del kwargs['max_length']
        del kwargs['choices']
        return name, path, args, kwargs

    def get_default(self):
        if self.has_default():
            if self.default is None:
                return None
            if isinstance(self.default, self.enum):
                return self.default
            return self.enum(self.default)
        return super().get_default()

    def get_choices(self, include_blank = True, blank_choice = BLANK_CHOICE_DASH):
        return [
            (i.value if i else i, display)
            for (i, display)
            in super().get_choices(include_blank, blank_choice)
        ]

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value.value if value else None

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if isinstance(value, self.enum):
            return value
        return self.enum(value) if value else None

    def get_prep_value(self, value):
        return value.value if value else None

    def formfield(self, **kwargs):
        # We want to make sure that a TypedChoiceField is used rather than a
        # normal ChoiceField
        defaults = { 'choices_form_class' : EnumChoiceField }
        defaults.update(kwargs)
        return super().formfield(**defaults)
