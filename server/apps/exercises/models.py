from django.db import models
from django.contrib.auth.models import User

from apps.participant.models import Participants
from apps.maps.models import Graphs, Concepts

class Exercises(models.Model):
    """
    Exercise storage
    """
    MULTIPLE = 0
    SHORT    = 1
    EXERCISE_TYPES = ( 
        ('Multiple choice', MULTIPLE),
        ('Short answer',    SHORT),
    )

    question = models.TextField()
    concepts = models.ManyToManyField(Concepts)
    qtype = models.CharField(max_length=1, 
                             choices=EXERCISE_TYPES,
                             default=MULTIPLE)

    def __unicode__(self):
        return u'%s' % (self.question)


class Responses(models.Model):
    """
    Correct answers and distractors for exercises
    """
    exercise = models.ForeignKey(Exercises)
    response = models.TextField()
    distract = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' % (self.response)


class Attempts(models.Model):
    """
    Store exercise attempts for every user
    """
    user = models.ForeignKey(User)
    participant = models.ForeignKey(Participants)
    graph = models.ForeignKey(Graphs)
    concept = models.ForeignKey(Concepts)
    exercise = models.ForeignKey(Exercises)
    correct = models.NullBooleanField()
    timestamp = models.DateTimeField(auto_now=True)
    submitted = models.BooleanField(default=False)

    def __unicode__(self):
        if self.submitted is True:
            return u'%s %i SUBMITTED %i' % (self.user.username, self.exercise, self.correct)
        return u'%s %i NOT SUBMITTED' % (self.user.username, self.exercise)

    def get_correctness(self):
        if self.submitted is True:
            return (self.concept.conceptId, self.correct)
        return None
