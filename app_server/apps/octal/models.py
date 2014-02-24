from django.db import models
from django.contrib.auth.models import User

from apps.user_management.models import Profile

class ExerciseConcepts(models.Model):
    """
    Skeleton to factor out concepts from exercise attempts
    """
    conceptId = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    def get_tag():
        return self.name


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
    concepts = models.ManyToManyField(ExerciseConcepts)
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
    uprofile = models.ForeignKey(Profile)
    concept = models.ForeignKey(ExerciseConcepts)
    exercise = models.ForeignKey(Exercises)
    correct = models.NullBooleanField()
    timestamp = models.DateTimeField(auto_now=True)
    submitted = models.BooleanField(default=False)

    def __unicode__(self):
        if self.submitted is True:
            return u'%s %i SUBMITTED %i' % (self.uprofile, self.exercise, self.correct)
        return u'%s %i NOT SUBMITTED' % (self.uprofile, self.exercise)

    def get_correctness(self):
        if self.submitted is True:
            return (self.concept.get_tag(), self.correct)
        return None
