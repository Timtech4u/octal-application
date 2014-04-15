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

    def _adjacency_list(self):
        adj = []
        for c in self.concepts_set.all():
            deps = [{"source": d.conceptId} for d in c.dependencies.all()]
            adj.append({ "id": c.conceptId, "title": c.name, "dependencies": deps })
        return adj
    flat = property(_adjacency_list)

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

