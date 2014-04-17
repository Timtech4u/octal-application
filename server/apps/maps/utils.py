from random import choice

class GraphIntegrityError(Exception):
    """
    An exception class for parsing a graph
    """
    def __init__(self, value):
        self.value = value


def graphCheck(adjacency_list):
    """
    Static method to verify the structure of a string is as expected
    """
    concepts = {}

    # keep track of postrequisite counts for every concept
    count = {}

    # keep track of forward and reverse edge direction at each concept
    check = {}

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
        concepts[cid] = { "deps": d, "name": c['title'] }
        check[cid] = 0
        count[cid] = -1

    # recurse through dependencies, if any back-edges exist, we have a cycle
    def _dfs_fwd_edge(cid):
        if cid not in concepts:
            raise GraphIntegrityError("unknown concept '%s'." % cid)
        count[cid] += 1
        if check[cid] is 2: return
        if check[cid] is 1: 
            raise GraphIntegrityError("cyclical graph structure. Some prerequisite of '%s' depends on it as a prerequisite." % cid)
        check[cid] = 1
        map(_dfs_fwd_edge, concepts[cid]['deps'])
        check[cid] = 2

    # check for cyclic dependencies and report an error if one exists
    for c in concepts: _dfs_fwd_edge(c)

    roots = [c for c in count if count[c]+len(concepts[c]["deps"]) is 0]
    if roots:
        raise GraphIntegrityError("one or more orphaned concepts (%s) with no pre- or post-requisites." % ', '.join(roots))

    return concepts

def generateSecret():
    """
    Generate a secret by randomly picking characters from a string
    """
    chars = "abcdefghjkmnpqrtuvwxyzABCDEFGHKMNPQRTUVWXYZ23456789?<>:!@#$%^&*()-_=+"
    return ''.join(choice(chars) for _ in range(16))
 
