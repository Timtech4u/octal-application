from django.db import models
from django.contrib.auth.models import User
import json

from apps.participant.models import Participants

class Concepts(models.Model):
    """
    Skeleton to factor out concepts from exercise attempts
    """
    conceptId = models.CharField(max_length=32)
    name = models.CharField(max_length=100)
    dependencies = models.ManyToManyField('self', symmetrical=False)

    def __unicode__(self):
        return self.name

    def _get_title(self):
        return self.name.encode('ascii')
    title = property(_get_title)


class Graph(models.Model):
    """
    Store the graph in the database.
    A NRDBMS like Mongo might be a good choice for this structure.
    However, as of this writing, Django does not support NRDBM 
    systems out of the box; it would require using the django-nonrel 
    fork. I'd rather maintain support for the main django branch at this time.
    http://django-mongodb-engine.readthedocs.org/en/latest/
    """
    name = models.CharField(max_length=100)
    concepts = models.ManyToManyField(Concepts)

    def _adjacency_list(self):
        adj = []
        for c in self.concepts.all():
            deps = [{"source": d.conceptId} for d in c.dependencies.all()]
            adj.append({ "id": c.conceptId, "title": c.name, "dependencies": deps })
        return adj
    flat = property(_adjacency_list)

    def __unicode__(self):
        return json.dumps(self.flat)


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


class ExerciseAttempts(models.Model):
    """
    Store exercise attempts for every user
    """
    user = models.ForeignKey(User)
    participant = models.ForeignKey(Participants)
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
            return (self.concept.get_tag(), self.correct)
        return None
