from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import admin

  
class Simulation(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

    
class SimulationRequest(models.Model):
    simulation = models.ForeignKey(Simulation)
    title = models.CharField(max_length=60)
    creator = models.ForeignKey(User, blank=True, null=True)
    computing_resource = models.CharField(max_length=128)
    remote_login = models.CharField(max_length=60)
    scratch_area = models.CharField(max_length=60)
    experiment_data = models.CharField(max_length=60)

    def __unicode__(self):
        return u"%s - %s - %s" % (self.creator, self.remote_login, self.title)
    