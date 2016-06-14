"""
Utilities for cross-db foreign keys.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ObjectDoesNotExist


class CrossDbGenericForeignKey(GenericForeignKey):
    """
    Generic foreign key that supports access accross databases.
    """
    def __get__(self, instance, instance_type = None):
        # Override __get__ to use the default database for the content type that
        # we are pointing to rather than the database of the object that holds
        # the foreign key
        if instance is None:
            return self
        try:
            return getattr(instance, self.cache_attr)
        except AttributeError:
            rel_obj = None
            f = self.model._meta.get_field(self.ct_field)
            ct_id = getattr(instance, f.get_attname(), None)
            if ct_id is not None:
                ct = self.get_content_type(id = ct_id, using = instance._state.db)
                try:
                    # Use objects instead of _base_manager so we pick up the correct
                    # DB via the router
                    rel_obj = ct.model_class().objects.get(pk = getattr(instance, self.fk_field))
                except ObjectDoesNotExist:
                    pass
            setattr(instance, self.cache_attr, rel_obj)
            return rel_obj
