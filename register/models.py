import uuid

from django.db import models


class InviteCode(models.Model):
    code = models.UUIDField(verbose_name="Invite code", default=uuid.uuid4, unique=True)
    used = models.BooleanField(verbose_name="Used?")
    used_by = models.CharField(max_length=191, verbose_name="Used by", blank=True, null=True)
    groups = models.TextField(verbose_name="Groups", blank=True, null=True)

    def __str__(self):
        if self.used:
            return "{} ({}) (used by {})".format(self.code, self.groups, self.used_by)
        return "{} ({})".format(self.code, self.groups)
