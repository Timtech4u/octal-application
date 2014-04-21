import matplotlib as mpl;
mpl.use('Agg')
import pymc as mc;
import pylab as pl;
import numpy as np;
#######ALL THESE PARAMETERS ARE ARBITRARY AND SHOULD BE TRAINED OR BETTER CHOSEN OR SOMETHING
#probability of a guess
pG = .2
#probability of a slip
pS = .3
#basic probability a student already knows a concept given we know they know all the prereqs.  Coinflip?  
pK = .5 #p(Knowledge)
#probability a student knows a concept given that they DON'T know ANY of the prereq(s)
pM = .05 #p(Magic)


def calculateProbability(name, dependencies, weights=0):
    #given that no specific weights are specified
    if weights == 0:
        weights = [1]*len(dependencies)
    assert len(weights) == len(dependencies)
    #get the current values of the dependencies
    return mc.Lambda(name, lambda dependencies=dependencies, weights=weights: (pK - pM) * sum(pl.multiply(dependencies,weights))/sum(weights) + pM)
        

def performInference(graph, responses):
    #this is a really hacky solution for now until I can spend more time figuring out how to do this more programatically 

    pStr = "p%s"

    def _build_probabilities(cid):
        #return memoized bernoulli variable
        if "_bp" in graph[cid]: return graph[cid]["_bp"]

        #hack since pymc seems to require ascii (and not unicode)
        cida = str(cid).encode('ascii')

        if graph[cid]["dependencies"]:
            # process dependencies first
            deps = map(_build_probabilities, graph[cid]["dependencies"])
            cp = calculateProbability(pStr % cida, deps)
            _bp = mc.Bernoulli(cida, cp, value=1)
        else:
            # roots get special treatment
            _bp = mc.Bernoulli(cida, .5, value=1)

        #memoize bernoulli variable
        graph[cid]["_bp"] = _bp
        return _bp

    concepts = map(_build_probabilities, graph)


    #variables = mc.Bernoulli('variables', .5, value=1)
    #concepts.append(variables);

    #pConditionals = calculateProbability('pConditionals', [variables])
    #conditionals = mc.Bernoulli('conditionals', pConditionals, value=1)
    #concepts.append(conditionals);

    otherQuestions = [];
    for example in responses:
        # more pymc ascii hacks
        cida = str(example[0]).encode('ascii')

        tmp = graph[example[0]]["_bp"]
        prob = mc.Lambda(pStr % cida, lambda tmp=tmp: pl.where(tmp, 1-pS, pG))
        otherQuestions.append(mc.Bernoulli(cida, prob, value=example[1], observed=True))
    
    ##################some simple tests##########
    
    model = mc.Model(concepts + otherQuestions);
    
    
    samples = mc.MCMC(model)
    knownNodes = [];
    samples.sample(1000)

    for concept in concepts:
        if concept.trace().mean() > 0.75:
            knownNodes.append(concept.__name__)
    return knownNodes

#this needs tweaking till it works  Try constructing the pl.where structure instead maybe?
#def buildDependencies(dependencies, name, idealP, nonIdealP, compensatoryP):
 #   p = 0;
 #   if len(dependencies) == 1:
 #       dep = dependencies[0];
 #       #for reference, the semantics of this are if dep=1, p=idealP, else if dep=0, p=nonIdealP
 #       p = mc.Lambda('', lambda dep=dep: pl.where(dep, idealP, nonIdealP))
 #   else:
 #       previousDep = buildDependencies(dependencies[1:len(dependencies)], name, idealP, nonIdealP, compensatoryP)
 #       dep = dependencies[0];
 #       #likewise with above, just with two variables that vary between 1 and zero, with the 1 case first
 #       p = (mc.Lambda('', lambda previousDep=previousDep, dep=dep: pl.where(dep, pl.where(previousDep,
 #           idealP, compensatoryP), pl.where(previousDep, compensatoryP, nonIdealP))))
 #   return p


         

#x = performInference([['algorithmic_complexity',0]])
