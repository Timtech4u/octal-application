from random import choice
import re

class GraphIntegrityError(Exception):
    """
    An exception class for parsing a graph
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value


def graphCheck(adjacency_list):
    """
    Static method to verify the structure of a string is as expected
    """
    concepts = {}

    # keep track of postrequisite counts for every concept
    count = {}

    # keep track of forward and reverse edge direction at each concept
    check = {}

    # keep track of any duplicate concept names
    dupes = {}

    # keys we expect in the input dictionary for every concept
    expected = ["title", "id", "dependencies"]

    # build a dictionary of concepts
    for index, c in enumerate(adjacency_list):
        # check that this concept contains all expected keys
        if any(key not in c for key in expected):
            raise GraphIntegrityError("missing key (title, id, or dependencies) from concept %d." % index)
        
        # attempt to pull dependencies
        try:
            d = [x['source'] for x in c['dependencies']]
        except KeyError:
            raise GraphIntegrityError("one or more dependencies in concept %d missing 'source' key." % index)

        cid = c['id']
        if cid in concepts:
            raise GraphIntegrityError("two concepts with ID '%s'; every ID must be unique." % cid)

        title = c['title'].strip()
        if len(title) > 32:
            raise GraphIntegrityError("concept name '%s' is longer than the limit of 32 characters." % title)

        # convert the title to tag name
        tag = re.sub('\W', '', '_'.join(title.lower().split()))

        concepts[cid] = { "deps":d, "name":c['title'], "tag":tag  }
        check[cid] = 0
        count[cid] = -1
        if tag in dupes:
            raise GraphIntegrityError("the concept names '%s' and '%s' are too similar." % (c['title'], dupes[tag]))
        dupes[tag] = c['title']

    # recurse through dependencies, if any back-edges exist, we have a cycle
    def _dfs_fwd_edge(cid):
        if cid not in concepts:
            raise GraphIntegrityError("unknown concept '%s'." % cid)
        count[cid] += 1
        if check[cid] is 2: return
        if check[cid] is 1: 
            raise GraphIntegrityError("cyclical graph structure. Some postrequisite of '%s' depends on it as a prerequisite." % 
                concepts[cid]['name'])
        check[cid] = 1
        map(_dfs_fwd_edge, concepts[cid]['deps'])
        check[cid] = 2

    # check for cyclic dependencies and report an error if one exists
    for c in concepts: _dfs_fwd_edge(c)

    roots = ['"%s"' % concepts[c]['name'] for c in count if count[c]+len(concepts[c]["deps"]) is 0]
    if roots:
        raise GraphIntegrityError("one or more orphaned concepts (%s) with no pre- or post-requisites." % ', '.join(roots))

    return concepts

def generateSecret(length=16):
    """
    Generate a secret by randomly picking characters from a string
    """
    chars = "abcdefghjkmnpqrtuvwxyzABCDEFGHKMNPQRTUVWXYZ23456789?<>!@#$%^&*()-_=+"
    return ''.join(choice(chars) for _ in range(length))
 
