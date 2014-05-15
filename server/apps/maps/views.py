from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.forms import HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.html import escape, strip_tags
from django.views.decorators.csrf import csrf_exempt

from lazysignup.decorators import allow_lazy_user

from forms import GraphForm, KeyForm
from models import Graphs, Concepts
from utils import graphCheck, generateSecret, require_edit_access, setEdit, canEdit

from ims_lti_py.tool_provider import DjangoToolProvider

from apps.research.models import Participants, Spectators, Studies
from apps.research.forms import StudyForm
from apps.research.utils import getParticipantByUID, handleSurveys, urlLanding, buildPIDs

import json

def display_all(request):
    graphs = Graphs.objects.filter(public=True).all()

    return render(request, "maps-all.html", {"maps":graphs})

def new_graph(request):
    f = {}
    if request.method == 'POST':
        # form submission
        f['graph'] = GraphForm(request.POST, prefix="graph")
        f['study'] = StudyForm(request.POST, prefix="study")

        if f['graph'].is_valid() and (not f['graph'].cleaned_data["study_active"] or f['study'].is_valid()):
            # woo all good
            g = f['graph'].save(commit=False)

            # hash graph's key
            g.secret = make_password(f['graph'].cleaned_data["secret"]);
            g.save()

            # build the graph's concepts
            g.build(f['graph'].cleaned_data["json_data"])

            # insert study data if applicable
            if f['graph'].cleaned_data["study_active"]:
                s = f['study'].save(commit=False)
                s.graph = g
                s.save()
                buildPIDs(s, f['study'].cleaned_data["pids"])
            else:
                # insert blank study
                Studies(graph=g).save()

            # all saved, provide edit access and forward to map
            setEdit(request, g.pk)
            return HttpResponseRedirect(reverse("maps:display", kwargs={"gid":g.pk}))
        f['error'] = f['graph'].errors.get('json_data')
    else:
        secrets = {'secret':generateSecret(),
                   'lti_key':generateSecret(8),
                   'lti_secret':generateSecret()}
        f['graph'] = GraphForm(initial=secrets, prefix="graph")
        f['study'] = StudyForm(prefix="study")

    return render(request, "maps-form.html", {'forms':f})

@allow_lazy_user
def display(request, gid):
    graph = get_object_or_404(Graphs, pk=gid)

    #OCTAL experiment: graph linearity based on user id
    p = None
    linear = 0
    participant = 0

    if graph.study_active:
        if request.user.is_authenticated():
            p = getParticipantByUID(request.user.pk, gid)

        #user has no participant ID yet, ask them for it
        if p is None:
            return HttpResponseRedirect(urlLanding(gid))

        # make sure participant completed the presurvey
        r = handleSurveys(p, gid)
        if r is not None: return HttpResponseRedirect(r)

        linear = int(p.linear)
        participant = int(p.isParticipant())

    return render(request, "map.html",{"full_graph_skeleton":graph, 
                              "graph_name": escape(strip_tags(graph.name)),
                              "linear":linear,
                              "participant":participant,
                              "editor":int(canEdit(request,gid)),
                              "study_active": int(graph.study_active),})

def auth(request, gid=""):
    """
    Allow a user to edit a unit for a session if correct secret
    """
    g = get_object_or_404(Graphs, pk=gid)

    fwd = request.GET.get('p', reverse('maps:display', kwargs={'gid':gid}))

    if request.method == 'POST':
        form = KeyForm(request.POST, graph=g, prefix="key")
        if form.is_valid():
            # user has entered a valid secret, forward back to URL
            setEdit(request, gid)
            return HttpResponseRedirect(fwd)
    else:
        form = KeyForm(graph=g, prefix="key")

    return render(request, "auth-form.html", {'key':form, 'gid':gid, 'fwd':fwd})


@require_edit_access
def edit(request, gid=""):
    g = get_object_or_404(Graphs, pk=gid)
    s = get_object_or_404(Studies, pk=gid)
    pids = ', '.join([p.pid for p in s.participants_set.all()])

    f = {}

    if request.method == 'POST':
        f['graph'] = GraphForm(request.POST, instance=g, prefix="graph")
        f['study'] = StudyForm(request.POST, instance=s, prefix="study", initial={'pids':pids})
        f['graph'].fields["json_input"].widget = HiddenInput()

        if f['graph'].is_valid() and (not f['graph'].cleaned_data["study_active"] or f['study'].is_valid()):
            # woo all good, save the graph and build its concepts
            g = f['graph'].save()
            g.build(f['graph'].cleaned_data["json_data"])

            # insert study data if applicable
            if f['graph'].cleaned_data["study_active"]:
                s = f['study'].save()

                if 'pids' in f['study'].changed_data:
                    # you asked for it! delete all participants
                    Participants.objects.filter(study=s).delete()
                    Spectators.objects.filter(study=s).delete()
                    buildPIDs(s, f['study'].cleaned_data["pids"])
            else:
                # delete all participants
                Participants.objects.filter(study=s).delete()
                Spectators.objects.filter(study=s).delete()

            return HttpResponseRedirect(reverse("maps:display", kwargs={"gid":g.pk}))
        f['error'] = f['graph'].errors.get('json_data')
    else:
        # prepare content; most data is provided by models
        gi = {'json_data':str(g)}
        f['graph'] = GraphForm(instance=g, prefix="graph", initial=gi)
        f['graph'].fields["json_input"].widget = HiddenInput()

        si = {'pids':pids}
        f['study'] = StudyForm(instance=s, prefix="study", initial=si)
        f['study'].fields['pids'].help_text = "<strong>Click above to edit. Note that editing the participant list will cause all participants to be deleted and re-created on the server.</strong><br />%s" % f['study'].fields['pids'].help_text;

    return render(request, "maps-form.html", {'forms':f, 'gid':gid})

@csrf_exempt
def lti(request, gid):
    graph = get_object_or_404(Graphs, pk=gid)

    if request.method != 'POST' or 'oauth_consumer_key' not in request.POST:
        return HttpResponse("Improper LTI request method", status=405)

    # confirm oauth credentials with ims_lti tool
    tool_provider = DjangoToolProvider(graph.lti_key, graph.lti_secret, request.POST)
    try:
        if tool_provider.valid_request(request) is False:
            raise PermissionDenied()
    except:
        raise PermissionDenied()

    # build username from userid
    userid = getattr(tool_provider, "user_id", None)
    if userid is None: raise PermissionDenied()

    username = "_%s" % (userid)

    # try to get the user
    user = authenticate(username=username)
    if user is None:
        u = User.objects.create_user(username=username)
        u.set_unusable_password()
        u.save()
        user = authenticate(username=username)

    # have the user ready to go, login
    login(request, user)

    # LTI user logged in, forward to map
    return HttpResponseRedirect(reverse("maps:display", kwargs={"gid":gid}))
