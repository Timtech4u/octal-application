from django.db import models

from apps.user_management.models import Profile

class ParticipantIDs(models.Model):
    """
    Stores valid participant IDs
    """
    pid = models.CharField(max_length=5, unique=True)
    linear = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%d' % (int(self.pid))

class Participants(models.Model):
    """
    Stores information about participants
    """
    uprofile = models.ForeignKey(Profile)
    pid = models.ForeignKey(ParticipantIDs)
    timestamp = models.DateTimeField(auto_now_add=True)
