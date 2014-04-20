from django import forms
from django.db import models
from django.contrib.auth.models import User
import re

from apps.maps.models import Graphs

class Studies(models.Model):
    """
    Stores information for a running study for a graph
    """
    graph = models.OneToOneField(Graphs, primary_key=True)
    complete = models.BooleanField(default=False)
    presurvey_url = models.TextField(blank=True)
    postsurvey_url = models.TextField(blank=True)

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
        return not hasattr(self, 'spectators')

class Spectators(models.Model):
    study = models.OneToOneField(Studies, primary_key=True)
    participant = models.OneToOneField(Participants)

    def _sid(self):
        return self.participant.pid
    pid = property(_sid)

class Logins(models.Model):
    """
    Stores information about participants
    A participant might use multiple browsers
    """
    user = models.ForeignKey(User)
    study = models.ForeignKey(Studies)
    participant = models.ForeignKey(Participants)
    timestamp = models.DateTimeField(auto_now_add=True)


class StudyForm(forms.ModelForm):
    pids = forms.CharField(label=("Participant List"),
            help_text=("List all participant IDs for the study, separated by a comma. The last participant ID is reserved as a spectator and will be used for non-participants. Whitespace (spaces, tabs, etc) is removed. Valid IDs are up to 32 alphanumeric characters."),
            widget=forms.Textarea(attrs={'cols':80, 'rows':10}))

    def clean_pids(self):
        """
        Validate the list of participants
        """
        # remove white space
        plist_str = "".join(self.cleaned_data['pids'].split())

        # validate string
        if re.search('[^0-9a-zA-Z,]', plist_str):
            raise forms.ValidationError("Please enter only letters, numbers, and commas.")

        # remove leading or trailing commas, split into list
        plist = re.sub('^,|,$', '', plist_str).split(',')

        # any duplicates?
        def _list_duplicates(seq):
            seen = set()
            seen_add = seen.add
            # adds all elements it doesn't know yet to seen and all other to seen_twice
            seen_twice = set( x for x in seq if x in seen or seen_add(x) )
            # turn the set into a list (as requested)
            return list( seen_twice )
        dupes = _list_duplicates(plist)
        if dupes: 
            raise forms.ValidationError("Please remove the duplicate participant IDs: %s" % ', '.join(dupes))

        if len(plist) < 2:
            raise forms.ValidationError("You must enter at least two participants.")

        return plist

    class Meta:
        model = Studies
        fields = ['complete', 'presurvey_url', 'postsurvey_url', 'pids']
        exclude = ['graph']
        labels = {
            'presurvey_url': ("Pre-Survey URL"),
            'postsurvey_url': ("Post-Survey URL"),
        }
        help_texts = {
            'complete': ("Check this box once the study has completed. Participants will be forwarded to the Post-Survey and subsequently given a screen thanking them for their participation."),
            'presurvey_url': ("Enter the URL of a pre-survey. If the URL contains '%s', the participant ID will replace it in the URL. Leave blank for no pre-survey."),
            'postsurvey_url': ("Participants will be automatically forwarded to this URL once the study has completed. Enter the URL of the post-survey. If the URL contains '%s', the participant ID will replace it in the URL. Leave blank for no post-survey."),
        }
        widgets = {
            'presurvey_url': forms.TextInput(attrs={'size':80}),
            'postsurvey_url': forms.TextInput(attrs={'size':80}),
        }
