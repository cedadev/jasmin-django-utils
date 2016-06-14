"""
Module defining a custom template tag for generating a mailto HREF to the support
address defined in the settings.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django.conf import settings
from django import template
from django.utils.http import quote


register = template.Library()

@register.simple_tag
def mailto_support(subject = None, prefix = None):
    """
    Template tag that outputs a ``mailto:...`` HREF for the ``SUPPORT_EMAIL`` defined
    in the settings.

    If subject is given, it is escaped and added to the HREF. If
    ``EMAIL_SUBJECT_PREFIX`` is defined in the settings, it is also prefixed to
    the subject, but can be overridden by specifying ``prefix``.
    """
    mailto = "mailto:" + settings.SUPPORT_EMAIL
    if subject:
        if prefix is None:
            prefix = getattr(settings, 'EMAIL_SUBJECT_PREFIX', '')
        mailto += "?subject=" + quote(prefix + subject)
    return mailto
