from django import forms
from django_bleach.forms import BleachField
from models import Problems, Responses

from apps.maps.models import Graphs, Concepts

def ProblemsFormSetFactory(g=None, post=None):
    def _form_factory(g):
        """
        A closure to restrict the dependencies to those in the supplied graph
        """
        class ProblemsForm(forms.ModelForm):
            answer = BleachField(label=("Correct Answer"),
                widget=forms.TextInput(attrs={'size': '80'}))
            distractor1 = BleachField(label=("Distrator"),
                required=False,
                widget=forms.TextInput(attrs={'size': '80'}))
            distractor2 = BleachField(label=("Distrator"),
                required=False,
                widget=forms.TextInput(attrs={'size': '80'}))
            distractor3 = BleachField(label=("Distrator"),
                required=False,
                widget=forms.TextInput(attrs={'size': '80'}))

            def __init__(self, *args, **kwargs):
                super(ProblemsForm, self).__init__(*args, **kwargs)
                self.fields['concepts'].queryset = Concepts.objects.filter(graph=g)
                self.fields['concepts'].help_text = "Most exercises apply only to a single concept. However, you may list multiple concepts if you wish the exercise to appear in more than one exercise set."
                # fill out answer and distractors if this problem has them
                if self.instance.id:
                    pset = Responses.objects.filter(problem=self.instance)
                    i = 1
                    for p in pset:
                        f = 'answer'
                        if p.distract and i < 4:
                            f = 'distractor%d' % i
                            i += 1
                        self.fields[f].initial = p.response

            class Meta:
                model = Problems
                labels = { 'qtype': ("Type"), }
                widgets = { 
                    'question': forms.Textarea(attrs={'cols':80, 'rows':4, 'class':'edit'}),
                }

        return ProblemsForm

    ProblemsFormSet = forms.models.inlineformset_factory(Graphs, Problems, extra=1)
    ProblemsForm = ProblemsFormSet(post, instance=g)
    ProblemsForm.form = _form_factory(g)
    return ProblemsForm

