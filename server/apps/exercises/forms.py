from django import forms
from models import Problems, Responses

from apps.maps.models import Graphs, Concepts

def ProblemsFormSetFactory(g=None, post=None):
    def _form_factory(g):
        """
        A closure to restrict the dependencies to those in the supplied graph
        """
        class ProblemsForm(forms.ModelForm):
            answer = forms.CharField(label=("Correct Answer"),
                widget=forms.TextInput(attrs={'size': '80'}))
            distractor1 = forms.CharField(label=("Distrator"),
                required=False,
                widget=forms.TextInput(attrs={'size': '80'}))
            distractor2 = forms.CharField(label=("Distrator"),
                required=False,
                widget=forms.TextInput(attrs={'size': '80'}))
            distractor3 = forms.CharField(label=("Distrator"),
                required=False,
                widget=forms.TextInput(attrs={'size': '80'}))

            def __init__(self, *args, **kwargs):
                super(ProblemsForm, self).__init__(*args, **kwargs)
                self.fields['concepts'].queryset = Concepts.objects.filter(graph=g)
                self.fields['concepts'].help_text = "Most exercises apply only to a single concept. However, you may list multiple concepts if you wish the exercise to appear in more than one exercise set."

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


