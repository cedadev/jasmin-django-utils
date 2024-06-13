"""Common django behaviours for JASMIN sites."""
import django.conf
import django.core.mail
import django.db.models
import polymorphic.models


class JoinJISCMailListBehaviour(polymorphic.models.PolymorphicModel):
    """
    Behaviour for joining a JISCMail list.

    Occurs only the first time a behaviour is applied for a user.
    """

    id = django.db.models.BigAutoField(primary_key=True)

    class Meta:
        verbose_name = "Join JISCMail List Behaviour"

    list_name = django.db.models.CharField(
        max_length=100,
        help_text="The name of the JISCMail mailing list to join",
        unique=True,
    )
    # This is the users who have joined already
    joined_users = django.db.models.ManyToManyField(
        django.conf.settings.AUTH_USER_MODEL, symmetrical=False, blank=True
    )

    def apply(self, user):
        # Don't join service users up to the mailing list
        if user.service_user:
            return
        # If the user is already in joined_users, there is nothing to do
        if self.joined_users.filter(pk=user.pk).exists():
            return
        django.core.mail.send_mail(
            f"Adding {user.email} ({user.get_full_name()}) to {self.list_name.lower()} mailing list",
            f"add {self.list_name.lower()} {user.email} {user.get_full_name()}",
            django.conf.settings.SUPPORT_EMAIL,
            django.conf.settings.JASMIN_SERVICES["JISCMAIL_TO_ADDRS"],
            fail_silently=True,
        )
        self.joined_users.add(user)
        self.save()

    def unapply(self, user):
        # users must now unsubscribe themselves
        pass

    def __str__(self):
        return f"Join JISCMail List <{self.list_name}>"