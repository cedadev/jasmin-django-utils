import oauth2_provider.contrib.rest_framework as oauth2_rf

from . import permissions


def spectacular_hide_admin_auth(endpoints, **kwargs):
    """
    Hide IsAdminUser permission from views.

    permissions.IsAdminUserOrTokenHasResourceScope confuses drf_spectacular and
    results in an incorrect schema. If this is the permission class remove it.
    """
    for endpoint in endpoints:
        if (len(endpoint[3].cls.permission_classes) == 1) and (
            endpoint[3].cls.permission_classes[0]
            is permissions.IsAdminUserOrTokenHasResourceScope
        ):
            endpoint[3].cls.permission_classes = [oauth2_rf.TokenHasResourceScope]
    return endpoints
