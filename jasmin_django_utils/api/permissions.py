"""Extra permission classes for the jasmin api."""
import oauth2_provider.contrib.rest_framework as oauth2_rf
import rest_framework.permissions as rf_perms


class IsAdminUserOrTokenHasResourceScope(rf_perms.OperandHolder):
    """Permission class to allow admin user access OR correctly scoped OAuth2 tokens."""

    def __init__(self):
        super().__init__(
            rf_perms.OR, oauth2_rf.TokenHasResourceScope, rf_perms.IsAdminUser
        )
