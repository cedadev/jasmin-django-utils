"""Extra permission classes for the jasmin api."""
import oauth2_provider.contrib.rest_framework as oauth2_rf
import rest_framework.permissions as rf_perms

# Create a permission class with allows the admin user access
# to everything AND correctly scoped OAuth2 tokens access where allowed.
IsAdminUserOrTokenHasResourceScope = (
    oauth2_rf.TokenHasResourceScope | rf_perms.IsAdminUser
)
