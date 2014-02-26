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

#TODO remove me
from django.views.decorators.csrf import csrf_exempt


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
    try:
        # try to recycle an unused attempt id
        attempt = ExerciseAttempts.objects.get(participant=p,
                                               exercise=ex,
                                               submitted=False)
        #filter(uprofile=user).filter(exercise=ex).get(submitted=False)
    except ExerciseAttempts.DoesNotExist:
        attempt = ExerciseAttempts(uprofile=user, participant=p, 
                                   exercise=ex, concept=con)
        attempt.save()
    return attempt.pk;


@allow_lazy_user
def handle_exercise_request(request, conceptId=""):
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
                    correct=True).values(
                    'exercise').distinct()

    # fetch a question the user hasn't yet answered correctly
    try:
        ex = Exercises.objects.filter(
                    concepts=eCon).exclude(
                    pk__in = [x['exercise'] for x in completed]).order_by(
                    '?')[:1].get()
    except Exercises.DoesNotExist:
        # seems they've gotten them all right! pick one at random
        try:
            #documentation warns order_by('?') may be slow
            ex = Exercises.objects.filter(concepts=eCon).order_by('?')[:1].get()
        except Exercises.DoesNotExist:
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
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')

@allow_lazy_user
@csrf_exempt #TODO remove me
def handle_exercise_attempt(request, attempt="", correct=""):
    uprof, pc = Profile.objects.get_or_create(pk=request.user.pk)
    p = getParticipantByUID(request.user.pk)

    # well, this shouldn't happen
    if p is None: return HttpResponse(status=401)

    try:
        # only inject attempts if we have not submitted for this attempt
        ex = ExerciseAttempts.objects.filter(participant=p).filter(submitted=False).get(pk=attempt)
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
        p = getParticipantByUID(request.user.pk)

        # well, this shouldn't happen
        if p is None: return HttpResponse(status=401)

        ex = ExerciseAttempts.objects.filter(participant=p).filter(submitted=True)
        r = [e.get_correctness() for e in ex.all()]
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
