from django.db import models
from django.contrib.auth.models import User

from apps.maps.models import Graphs

class Studies(models.Model):
    """
    Stores information for a running study for a graph
    """
    graph = models.OneToOneField(Graphs)
    complete = models.BooleanField(default=False)
    spectator = models.ForeignKey('Participants')
    presurvey_url = models.TextField()
    postsurvey_url = models.TextField()

    def preSurveyURL(self, pid):
        try:
            return self.presurvey_url % pid
        except TypeError:
            return self.presurvey_url

    def postSurveyURL(self, pid):
        try:
            return self.postsurvey_url % pid
        except TypeError:
            return self.postsurvey_url

    def _spectatorID(self):
        return self.spectator.pid
    spectatorID = property(_spectatorID)

class Participants(models.Model):
    """
    Stores valid participant IDs
    """
    pid = models.CharField(max_length=32)
    study = models.ForeignKey(Studies)
    linear = models.BooleanField(default=False)
    presurvey = models.BooleanField(default=False)
    postsurvey = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%d' % (int(self.pid))

    def isParticipant(self):
        return self.pid != self.study.spectatorID

class Logins(models.Model):
    """
    Stores information about participants
    A participant might use multiple browsers
    """
    user = models.ForeignKey(User)
    study = models.ForeignKey(Studies)
    participant = models.ForeignKey(Participants)
    timestamp = models.DateTimeField(auto_now_add=True)
