from django import forms
from models import Graphs, Concepts
from utils import graphCheck, GraphIntegrityError

import json

class GraphForm(forms.ModelForm):
    json_input = forms.BooleanField(label=("JSON Input"), required=False,
            help_text=("Check this box to define the graph with raw JSON instead of the graph editor."))
    json_data = forms.CharField(label=("Graph JSON"), required=False,
            help_text=("Copy-paste or type the JSON representation of your graph here."),
            widget=forms.Textarea(attrs={'cols':80, 'rows':10}))

    def clean_json_data(self):
        """
        Validate JSON as being kmap structure
        """
        json_data = self.cleaned_data['json_data']
        try: 
            graph_list = json.loads(json_data) 
            return graphCheck(graph_list)
        except ValueError:
            raise forms.ValidationError("Error: malformed JSON")
        except GraphIntegrityError as e:
            raise forms.ValidationError("Error: %(val)s", params={'val':e})

    class Meta:
        model = Graphs
        fields = ['name', 'description', 'public', 'study_active', 'json_input', 'json_data', 'secret']
        labels = {
            'name': ("Graph Name"),
            'study_active': ("Research study"),
        }
        help_texts = {
            'public': ("Public maps are displayed on the map list. Private maps will still be publicly viewable by anyone with the URL."),
            'secret': ("The secret is used to modify the graph in the future. Please remember the value of this field!"),
            'study_active': ("Check this only if you plan to use this map as part of a research investigation."),
        }
        widgets = {
            'name': forms.TextInput(attrs={'size':40}),
            'description': forms.Textarea(attrs={'cols':40, 'rows':2}),
            'secret': forms.HiddenInput(),
        }

def NodesFormSetFactory(g=None, post=None):
    def _form_factory(g):
        """
        A closure to restrict the dependencies to those in the supplied graph
        """
        class NodesForm(forms.ModelForm):
            def __init__(self, *args, **kwargs):
                super(NodesForm, self).__init__(*args, **kwargs)
                self.fields['dependencies'].queryset = Concepts.objects.filter(graph=g)
                self.fields['dependencies'].required = False
            class Meta:
                model = Concepts
                #fields = ['name', 'conceptId', 'dependencies']
                exclude = ['conceptId']
                labels = {
                    #'conceptId': ("Concept ID"),
                    'name': ("Concept Title"),
                    'dependencies': ("Prerequisites"),
                }
                help_texts = {
                    #'conceptId': ("A unique identifier for a concept. Numbers, lowercase letters, and underscore are allowed."),
                    'dependencies': ("A list of other concept IDs that are a prerequisite for this concept."),
                }
        return NodesForm

    NodesFormSet = forms.models.inlineformset_factory(Graphs, Concepts)
    NodesForm = NodesFormSet(post, instance=g, prefix="nodes")
    NodesForm.form = _form_factory(g)
    return NodesForm

class KeyForm(forms.Form):
    """
    This form passes along data to ensure the user has authority to edit a map
    """
    secret = forms.CharField(max_length=16, label=("Secret Key"), 
                             widget=forms.TextInput(attrs={
                                 'autocomplete':'off',
                                 'autocorrect':'off',
                                 'autocapitalize':'off',
                                 'autofocus':'autofocus',
                                 }))
    edited = forms.BooleanField(required=False, initial=False, 
                                widget=forms.HiddenInput())

    def clean(self):
        """
        When validating the form, compare the key against the graph's secret
        """
        cleaned_data = super(KeyForm, self).clean()
        if self._graph.secret != cleaned_data.get("secret"):
            raise forms.ValidationError("Incorrect secret")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self._graph = kwargs.pop('graph')
        super(KeyForm, self).__init__(*args, **kwargs)
