import json
import requests, csv

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from lazysignup.decorators import allow_lazy_user

from apps.octal.models import Exercises, Responses, ExerciseAttempts, ExerciseConcepts
from apps.cserver_comm.cserver_communicator import get_full_graph_json_str, get_id_to_concept_dict
from apps.user_management.models import Profile

from apps.octal.knowledgeInference import performInference
from apps.participant.utils import getParticipantByUID


def get_octal_app(request):
    if request.user.is_authenticated():
        uprof, created = Profile.objects.get_or_create(pk=request.user.pk)
        lset = set()
        sset = set()
        [lset.add(lc.id) for lc in uprof.learned.all()]
        [sset.add(sc.id) for sc in uprof.starred.all()]
        concepts = {"concepts": [{"id": uid, "learned": uid in lset, "starred": uid in sset} for uid in lset.union(sset)]}
    else:
        concepts = {"concepts": []}
    return render_to_response("octal-app.html", 
                              {
                                "full_graph_skeleton": get_full_graph_json_str(),
                                "user_data": json.dumps(concepts)
                              },
                              context_instance=RequestContext(request))

def fetch_attempt_id(user, p, con, ex):
    attempt = ExerciseAttempts.objects.filter(participant=p)
    if not p.isParticipant(): attempt = attempt.filter(uprofile=user)

    try:
        # try to recycle an unused attempt id
        attempt = attempt.get(exercise=ex, submitted=False)
    except ExerciseAttempts.DoesNotExist:
        attempt = ExerciseAttempts(uprofile=user, participant=p, 
                                   exercise=ex, concept=con)
        attempt.save()
    return attempt.pk;


@allow_lazy_user
def handle_exercise_request(request, conceptId="", qid=""):
    #does the requested concept exist?
    concept_dict = get_id_to_concept_dict()
    if conceptId not in concept_dict: 
        return HttpResponse(status=422)

    user, pcreated = Profile.objects.get_or_create(pk=request.user.pk)
    eCon, ccreated = ExerciseConcepts.objects.get_or_create(conceptId=conceptId,
                                name=concept_dict[conceptId]['tag'])
    p = getParticipantByUID(request.user.pk)

    # well, this shouldn't happen
    if p is None: return HttpResponse(status=401)

    completed = ExerciseAttempts.objects.filter(
                    participant=p).filter(
                    concept=eCon).filter(
                    correct=True)

    # we need to differentiate non-participants by their user profile id
    if not p.isParticipant(): completed = completed.filter(uprofile=user)
    
    completed = completed.values('exercise').distinct()

    numComplete = completed.count()

    # filter out questions the user has answered
    ex = Exercises.objects.filter(concepts=eCon).exclude(
            pk__in = [x['exercise'] for x in completed])

    # how many are in this set?
    numRemaining = ex.count()

    # filter out the current question, if provided and if possible
    if qid and numRemaining > 1: ex = ex.exclude(pk=int(qid))

    # if student has completed all, pick one from the total set
    if numRemaining == 0: ex = Exercises.objects.filter(concepts=eCon)

    # fetch a question the user hasn't yet answered correctly
    try:
        ex = ex.order_by('?')[:1].get()
    except Exercises.DoesNotExist:
        # uh oh, none to give?
        return HttpResponse(status=404) 

    # fetch the question answers
    try:
        r = Responses.objects.filter(exercise=ex).order_by("distract")
    except Responses.DoesNotExist:
        return HttpResponse(status=404)

    data = {
        'qid': ex.pk,
        'h': ex.question,
        't': ex.qtype,
        'a': [x.response for x in r],
        'aid': fetch_attempt_id(user, p, eCon, ex),
        'cr': numRemaining, # expose how many left they have
        'ct': numComplete+numRemaining, # expose how many total questions in concept
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')

@allow_lazy_user
def handle_exercise_attempt(request, attempt="", correct=""):
    uprof, pc = Profile.objects.get_or_create(pk=request.user.pk)
    p = getParticipantByUID(request.user.pk)

    # well, this shouldn't happen
    if p is None: return HttpResponse(status=401)

    exs = ExerciseAttempts.objects.filter(participant=p).filter(submitted=False)
    if not p.isParticipant(): exs.filter(uprofile=uprof)

    try:
        # only inject attempts if we have not submitted for this attempt
        ex = exs.get(pk=attempt)
    except ExerciseAttempts.DoesNotExist, ExerciseAttempts.MultipleObjectsReturned:
        ex = None

    if request.method == "GET":
        return HttpResponse(ex)
    elif request.method == "PUT":
        # only accept data if we were waiting for it
        if ex is None:
            return HttpResponse(status=401)

        correctness = True if int(correct) is 1 else False

        ex.correct = correctness
        ex.submitted = True
        ex.save()

        # provide a new attempt id if it was incorrect
        if correctness:
            return HttpResponse()
        else:
            return HttpResponse(fetch_attempt_id(uprof, p, ex.concept, ex.exercise))
            
    else:
        return HttpResponse(status=405)

@allow_lazy_user
def handle_knowledge_request(request, conceptID=""):
    if request.method == "GET":
        user, pcreated = Profile.objects.get_or_create(pk=request.user.pk)
        p = getParticipantByUID(request.user.pk)

        # well, this shouldn't happen
        if p is None: return HttpResponse(status=401)

        ex = ExerciseAttempts.objects.filter(participant=p).filter(submitted=True)
        if not p.isParticipant(): ex = ex.filter(uprofile=user)
        r = [e.get_correctness() for e in ex]
        inferences = performInference(r)
        return HttpResponse(json.dumps(inferences), mimetype='application/json')
    else:
        return HttpResponse(status=405)

def build_exercise_db(request):
    concept_dict = get_id_to_concept_dict()
    concepts = {}
    for c in concept_dict:
        tag = concept_dict[c]['tag']
        concepts[tag],t = ExerciseConcepts.objects.get_or_create(conceptId=c, 
                                        name=tag)

    gdoc = requests.get('https://docs.google.com/spreadsheet/pub?key=0ApfeFyIuuj_MdF9ZS3hXU0pUN0NnMDVIcHFkTlN6V0E&single=true&gid=0&output=csv')

    if gdoc.status_code != 200:
        return HttpResponse(status=404)

    # parse the gdoc CSV file into a dictionary
    exercises = csv.DictReader(gdoc.content.splitlines())

    for e in exercises:
        ex,t = Exercises.objects.get_or_create(pk=e['qid'])

        # update question text
        ex.question = e['question']

        # add concepts to the exercise (concepts separated by |)
        ex.concepts = [concepts[x] for x in e['concepts'].split('|')]

        # TODO: fix special case
        if int(e['qid']) is 0:
            ex.qtype = ex.SHORT
            ex.save()
            continue

        ex.save()

        # destroy existing answers, if any
        Responses.objects.filter(exercise=ex).delete()

        # add answer and distractors
        Responses.objects.get_or_create(exercise=ex, response=e['ans'])
        for d in [e['d1'], e['d2'], e['d3']]:
            d = d.strip()
            if not d: continue
            Responses.objects.get_or_create(exercise=ex, response=d, distract=True)

    return HttpResponse("Done")
