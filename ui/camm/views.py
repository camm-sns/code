from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils import timezone

from camm.models import Simulation, SimulationRequest

    
class SimulationType(generic.ListView):
    template_name = 'camm/simulation_type.html'
    context_object_name = 'simulation_list'

    def get_queryset(self):
        return Simulation.objects.all()

def simulation_form(request):
    if 'choice' in request.GET and request.GET['choice']:
        choice = request.GET['choice']
        return render(request, 'camm/simulation_form.html',
             {'choice': choice})
    else:
        return render(request, 'camm/simulation_form.html', {'error': True})


def submit(request):           
    error = ""
    title = ""
    user = ""
    scratch_dir = ""
    experiment_data =""
    
    if 'go' in request.GET and request.GET['go']:
        execute = request.GET['go']
        
        if 'title' not in request.GET or not request.GET['title']:
            error = "title"
        else:
            title = request.GET['title']
            
        if 'user' not in request.GET or not request.GET['user']:
            if error:
                error += ", "
            error += "user"
        else:
            user = request.GET['user']
            
        if 'scratch_dir' not in request.GET or not request.GET['scratch_dir']:
            if error:
                error += ", "
            error += "scratch_dir"
        else:
            scratch_dir = request.GET['scratch_dir']
            
        if 'experiment_data' not in request.GET or not request.GET['experiment_data']:
            if error:
                error += ", "
            error += "experiment_data"
        else:
            experiment_data = request.GET['experiment_data']
            
        if error:
            return render(request, 'camm/simulation_form.html', {'error_message': error, 'user': user, 'title': title, 'scratch_dir': scratch_dir, 'experiment_data': experiment_data})
        else:
            return render(request, 'camm/simulation_results.html',  {'execute': execute, 'user': user, 'title': title, 'scratch_dir': scratch_dir, 'experiment_data': experiment_data})

    
    elif 'pause' in request.GET and request.GET['pause']:
        execute = request.GET['pause']
    elif 'resume' in request.GET and request.GET['resume']:
        execute = request.GET['resume']
    elif 'stop' in request.GET and request.GET['stop']:
        execute = request.GET['stop']
    else:
        return render(request, 'camm/simulation_form.html', {'error': True})
    


