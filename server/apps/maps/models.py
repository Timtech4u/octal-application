from django.db import models
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
    secret = models.CharField(max_length=128)
    study_active = models.BooleanField(default=False)
    lti_key = models.CharField(max_length=8)
    lti_secret = models.CharField(max_length=16)

    def _adjacency_list(self):
        """
        Builds an adjacency list in the hierarchy mimicking Metacademy
        This is well-suited to be dumped as a JSON and used by kmapjs
        [ { id:pk, tag:tag, title:name, dependencies:[tags] }, .. ]
        """
        adj = []
        for c in self.concepts_set.all():
            deps = [{"source": str(d.id)} for d in c.dependencies.all()]
            adj.append({ "id": str(c.id), "tag": c.tag, "title": c.name, "dependencies": deps })
        return adj
    flat = property(_adjacency_list)

    def _concept_dict(self):
        """
        Builds a dictionary with concept IDs as keys
        { conceptID: { title: conceptName, dependencies: [conceptIDs] },[..] }
        """
        concepts = {}
        for c in self.concepts_set.all():
            deps = [d.id for d in c.dependencies.all()]
            concepts[c.id] = { "tag": c.tag, "title": c.name, "dependencies": deps }
        return concepts
    concept_dict = property(_concept_dict)

    def build(self, concepts):
        # mark old concepts
        Concepts.objects.filter(graph=self).update(tag="")

        generated = {}
        # recurse through all dependencies, memoizing generated concepts
        def _build(cid):
            if cid in generated: return generated[cid]
            # replace concept data if it already exists
            try:
                db = Concepts.objects.get(id=int(cid), graph=self)
            except ValueError, Concepts.DoesNotExist:
                db = Concepts(graph=self)
            db.tag = concepts[cid]["tag"]
            db.name = concepts[cid]["name"]
            db.save()
            for depid in concepts[cid]["deps"]:
                db.dependencies.add(_build(depid))
            generated[cid] = db
            return db
        map(_build, concepts)

        # flush old concepts
        Concepts.objects.filter(graph=self, tag="").delete()

    def __unicode__(self):
        return json.dumps(self.flat)

class Concepts(models.Model):
    """
    Skeleton to factor out concepts from exercise attempts
    """
    tag = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    dependencies = models.ManyToManyField('self', symmetrical=False)
    graph = models.ForeignKey(Graphs)

    def __unicode__(self):
        return self.name

    def _get_title(self):
        return self.name.encode('ascii')
    title = property(_get_title)


