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
        

def performInference(responses):
    #this is a really hacky solution for now until I can spend more time figuring out how to do this more programatically 

    concepts = [];        
    ###########hardcoding our graph in for some testing - fix this###############
    variables = mc.Bernoulli('variables', .5, value=1)
    concepts.append(variables);

    pConditionals = calculateProbability('pConditionals', [variables])
    conditionals = mc.Bernoulli('conditionals', pConditionals, value=1)
    concepts.append(conditionals);

    pVariableMutation = calculateProbability('pVariableMutation',[variables])
    variable_mutation = mc.Bernoulli('variable_mutation', pVariableMutation, value=1)
    concepts.append(variable_mutation);

    pLoops = calculateProbability('pLoops', [variable_mutation, conditionals])
    loops = mc.Bernoulli('loops', pLoops, value=1)
    concepts.append(loops);

    pFunctions = calculateProbability('pFunctions', [variables])
    functions = mc.Bernoulli('functions', pFunctions, value=1)
    concepts.append(functions);

    pLists = calculateProbability('pLists', [loops])
    lists = mc.Bernoulli('lists', pLists, value=1)
    concepts.append(lists);

    pTreeRecursion = calculateProbability('pTreeRecursion', [functions])
    tree_recursion = mc.Bernoulli('tree_recursion', pTreeRecursion, value=1)
    concepts.append(tree_recursion);

    pTailRecursion = calculateProbability('pTailRecursion', [functions])
    tail_recursion = mc.Bernoulli('tail_recursion', pTailRecursion, value=1)
    concepts.append(tail_recursion);

    pFractals = calculateProbability('pFractals', [tail_recursion, tree_recursion])
    fractals = mc.Bernoulli('fractals', pFractals, value=1)
    concepts.append(fractals);

    pConcurrency = calculateProbability('pConcurrency', [functions])
    concurrency = mc.Bernoulli('concurrency', pConcurrency, value=1)
    concepts.append(concurrency);

    pAComplexity = calculateProbability('pAComplexity', [lists, tail_recursion, tree_recursion])
    algorithmic_complexity = mc.Bernoulli('algorithmic_complexity', pAComplexity, value=1)
    concepts.append(algorithmic_complexity);

    pMidterm = calculateProbability('pMidterm', [algorithmic_complexity, fractals, concurrency, tail_recursion, tree_recursion, lists, functions])
    midterm = mc.Bernoulli('midterm', pMidterm, value=1)
    concepts.append(midterm);
    ########################################################################
    
    pQuestion1 = mc.Lambda('pQuestion1', lambda lists=lists: pl.where(lists, 1-pS, pG))
    question1 = mc.Bernoulli('question1', pQuestion1, value=[1,1,1,1], observed=True)
    
    pQuestion2 = mc.Lambda('pQuestion2', lambda tail_recursion=tail_recursion: pl.where(tail_recursion, 1-pS, pG))
    question2 = mc.Bernoulli('question2', pQuestion2, value=[1, 1, 1, 1, 1], observed=True)

    pQuestion3 = mc.Lambda('pQuestion3', lambda concurrency=concurrency: pl.where(concurrency, 1-pS, pG))
    question3 = mc.Bernoulli('question3', pQuestion3, value=[1,1,1,1,1], observed=True)

    pQuestion4 = mc.Lambda('pQuestion4', lambda variables=variables: pl.where(variables, 1-pS, pG))
    question4 = mc.Bernoulli('question4', pQuestion4, value=1, observed=True)

    pQuestion5 = mc.Lambda('pQuestion5', lambda conditionals=conditionals: pl.where(conditionals, 1-pS, pG))
    question5 = mc.Bernoulli('question5', pQuestion5, value=1, observed=True)

    pQuestion6 = mc.Lambda('pQuestion6', lambda loops=loops: pl.where(loops, 1-pS, pG))
    question6 = mc.Bernoulli('question6', pQuestion6, value=[1,1,1], observed=True)

    #pQuestion7 = mc.Lambda('pQuestion7', lambda algorithmic_complexity=algorithmic_complexity: pl.where(algorithmic_complexity, 1-pS, pG))
    #question7 = mc.Bernoulli('question7', pQuestion7, value=[0], observed=True)

    otherQuestions = [];
    for example in responses:
        tmp = vars()[example[0]]
        prob = mc.Lambda("p" + example[0], lambda tmp=tmp: pl.where(tmp, 1-pS, pG))
        otherQuestions.append(mc.Bernoulli(example[0], prob, value=example[1], observed=True))
    
    ##################some simple tests##########
    
    model = mc.Model(concepts + [question1, question2, question3, question4, question5, question6] + otherQuestions);
    
    
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
