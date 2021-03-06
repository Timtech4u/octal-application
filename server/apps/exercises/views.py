from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from models import Problems, Responses, Attempts
from forms import ProblemsFormSetFactory

from apps.maps.models import Graphs, Concepts
from apps.maps.utils import require_edit_access
from apps.research.utils import getParticipantByUID, studyFilter

import json, requests, csv

def fetch_attempt_id(u, p, g, con, pr):
    attempt = studyFilter(g, p, u, Attempts.objects.filter(graph=g))

    try:
        # try to recycle an unused attempt id
        attempt = attempt.get(problem=pr, submitted=False)
    except Attempts.DoesNotExist:
        attempt = Attempts(user=u, participant=p, graph=g, problem=pr, concept=con)
        attempt.save()
    return attempt.pk;


def fetch_ex(request, gid="", tag="", qid=""):
    #does the requested concept exist in the graph?
    g = get_object_or_404(Graphs, pk=gid)
    eCon = get_object_or_404(Concepts, graph=g, tag=tag)

    if not request.user.is_authenticated(): return HttpResponse(status=403)
    user, ucreated = User.objects.get_or_create(pk=request.user.pk)

    completed = Attempts.objects.filter(concept=eCon).filter(correct=True)

    # we need to collect data by participant IDs for studies!
    p = getParticipantByUID(request.user.pk, gid)
    if g.study_active and p is None:
        return HttpResponse(status=401)

    completed = studyFilter(g, p, user, completed).values('problem').distinct()

    numComplete = completed.count()

    # filter out questions the user has answered
    pr = Problems.objects.filter(concepts=eCon).exclude(
            pk__in = [x['problem'] for x in completed])

    # how many are in this set?
    numRemaining = pr.count()

    # filter out the current question, if provided and if possible
    if qid and numRemaining > 1: pr = pr.exclude(id=int(qid))

    # if student has completed all, pick one from the total set
    if numRemaining == 0: pr = Problems.objects.filter(concepts=eCon)

    # fetch a question the user hasn't yet answered correctly
    try:
        pr = pr.order_by('?')[:1].get()
    except Problems.DoesNotExist:
        # uh oh, none to give?
        return HttpResponse(status=404) 

    # fetch the question answers
    try:
        r = Responses.objects.filter(problem=pr).order_by("distract")
    except Responses.DoesNotExist:
        return HttpResponse(status=404)

    data = {
        'qid': pr.id,
        'h': pr.question,
        't': pr.qtype,
        'a': [x.response for x in r],
        'aid': fetch_attempt_id(user, p, g, eCon, pr),
        'cr': numRemaining, # expose how many left they have
        'ct': numComplete+numRemaining, # expose how many total questions in concept
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')

def set_attempt(request, gid="", attempt="", correct=""):
    g = get_object_or_404(Graphs, pk=gid)

    if not request.user.is_authenticated(): return HttpResponse(status=403)
    u, pc = User.objects.get_or_create(pk=request.user.pk)

    attempts = Attempts.objects.filter(submitted=False).filter(graph=g)

    p = getParticipantByUID(request.user.pk, gid)
    if g.study_active and p is None:
        return HttpResponse(status=401)

    attempts = studyFilter(g, p, u, attempts)

    try:
        # only inject attempts if we have not submitted for this attempt
        attempt = attempts.get(pk=attempt)
    except Attempts.DoesNotExist, Attempts.MultipleObjectsReturned:
        attempt = None

    if request.method == "GET":
        return HttpResponse(pr)
    elif request.method == "PUT":
        # only accept if we're waiting for data
        if attempt is None:
            return HttpResponse(status=401)

        correctness = True if int(correct) is 1 else False

        attempt.correct = correctness
        attempt.submitted = True
        attempt.save()

        # provide a new attempt id if it was incorrect
        if correctness:
            return HttpResponse()
        else:
            return HttpResponse(fetch_attempt_id(u, p, g, attempt.concept, attempt.problem))
            
    else:
        return HttpResponse(status=405)

@require_edit_access
def edit(request, gid=""):
    g = get_object_or_404(Graphs, pk=gid)
    #ans = ', '.join([p.pid for p in s.participants_set.all()])

    if request.method == 'POST':
        forms = ProblemsFormSetFactory(g, post=request.POST)

        # we require at least one exercise
        forms[0].empty_permitted = False

        if forms.is_valid():
            for f in forms:
                if not f.has_changed(): continue

                # manually delete the form if selected
                if f in forms.deleted_forms:
                    instance = f.instance
                    if instance.pk: instance.delete()
                    continue

                p = f.save()

                # destroy existing answers, if any
                Responses.objects.filter(problem=p).delete()

                # save the answer
                ans = f.cleaned_data['answer']
                Responses(problem=p, response=ans).save()

                # build and save distractors
                distractors = [d.strip() for k,d in f.cleaned_data.iteritems() if k.startswith('distractor')]
                for d in distractors:
                    if not d: continue
                    Responses(problem=p, response=d, distract=True).save()

            return HttpResponseRedirect(reverse("maps:display", kwargs={"gid":gid}))
    else:
        forms = ProblemsFormSetFactory(g)

    return render(request, "exercises-form.html", 
                    {'forms':forms, 'gid':gid, 'gname':g.name})

def build(request, gid=""):
    g = get_object_or_404(Graphs, pk=gid)

    graph_concepts = g.concepts_set.all()
    concepts = {}
    for c in graph_concepts:
        cid = c.tag
        concepts[cid] = c

    gdoc = requests.get('https://docs.google.com/spreadsheet/pub?key=0ApfeFyIuuj_MdF9ZS3hXU0pUN0NnMDVIcHFkTlN6V0E&single=true&gid=0&output=csv')

    if gdoc.status_code != 200:
        return HttpResponse(status=404)

    # parse the gdoc CSV file into a dictionary
    exercises = csv.DictReader(gdoc.content.splitlines())

    for e in exercises:
        #pr,t = Problems.objects.get_or_create(graph=g, qid=e['qid'])
        pr = Problems.objects.create(graph=g)

        # update question text
        pr.question = e['question']

        # add concepts to the exercise (concepts separated by |)
        pr.concepts = [concepts[x] for x in e['concepts'].split('|')]

        pr.save()

        # destroy existing answers, if any
        Responses.objects.filter(problem=pr).delete()

        # add answer and distractors
        Responses(problem=pr, response=e['ans']).save()
        for d in [e['d1'], e['d2'], e['d3']]:
            d = d.strip()
            if not d: continue
            Responses(problem=pr, response=d, distract=True).save()

    return HttpResponse("Done")
