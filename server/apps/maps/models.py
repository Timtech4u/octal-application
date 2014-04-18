from django.db import models
from django import forms
from utils import graphCheck, GraphIntegrityError
import json

class Graphs(models.Model):
    """
    Store the graph in the database.
    A NRDBMS like Mongo might be a good choice for this structure.
    However, as of this writing, Django does not support NRDBM 
    systems out of the box; it would require using the django-nonrel 
    fork. I'd rather maintain support for the main django branch at this time.
    http://django-mongodb-engine.readthedocs.org/en/latest/
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    public = models.BooleanField(default=True)
    secret = models.CharField(max_length=16)
    study_active = models.BooleanField(default=False)

    def _adjacency_list(self):
        """
        Builds an adjacency list in the hierarchy mimicking Metacademy
        This is well-suited to be dumped as a JSON and used by kmapjs
        [ { id: conceptID, title: conceptName, dependencies: [conceptIDs]} ]
        """
        adj = []
        for c in self.concepts_set.all():
            deps = [{"source": d.conceptId} for d in c.dependencies.all()]
            adj.append({ "id": c.conceptId, "title": c.name, "dependencies": deps })
        return adj
    flat = property(_adjacency_list)

    def _concept_dict(self):
        """
        Builds a dictionary with concept IDs as keys
        { conceptID: { title: conceptName, dependencies: [conceptIDs] },[..] }
        """
        concepts = {}
        for c in self.concepts_set.all():
            deps = [d.conceptId for d in c.dependencies.all()]
            concepts[c.conceptId] = { "title": c.name, "dependencies": deps }
        return concepts
    concept_dict = property(_concept_dict)

    def build(self, concepts):
        generated = {}
        # recurse through all dependencies, memoizing generated concepts
        def _build(cid):
            if cid in generated: return generated[cid]
            db = Concepts(graph=self, conceptId=cid, name=concepts[cid]["name"])
            db.save()
            for depid in concepts[cid]["deps"]:
                db.dependencies.add(_build(depid))
            generated[cid] = db
            return db
        map(_build, concepts)

    def __unicode__(self):
        return json.dumps(self.flat)

class Concepts(models.Model):
    """
    Skeleton to factor out concepts from exercise attempts
    """
    conceptId = models.CharField(max_length=32)
    name = models.CharField(max_length=100)
    dependencies = models.ManyToManyField('self', symmetrical=False)
    graph = models.ForeignKey(Graphs)

    def __unicode__(self):
        return self.name

    def _get_title(self):
        return self.name.encode('ascii')
    title = property(_get_title)

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
    secret = forms.CharField(max_length=16, label=("Secret Key"))
    edited = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())

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
