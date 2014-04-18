from django import forms
from models import Graphs

class GraphForm(forms.ModelForm):
    graph_json = forms.CharField(label=("Graph JSON"),
            help_text=("Copy-paste or type the JSON representation of your graph here."),
            widget=forms.Textarea(attrs={'cols':80, 'rows':10}))

    def clean_graph_json(self):
        """
        Validate the JSON as being a kmap structure
        """
        json_data = self.cleaned_data['graph_json']
        try:
            graph_list = json.loads(json_data)
        except ValueError:
            raise forms.ValidationError("Error: malformed JSON")

        try:
            parsed_concepts = graphCheck(graph_list)
        except GraphIntegrityError as e:
            raise forms.ValidationError("Error: %(v)s", params={'v':e.value})

        return parsed_concepts

    class Meta:
        model = Graphs
        fields = ['name', 'description', 'public', 'graph_json', 'study_active', 'secret']
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
