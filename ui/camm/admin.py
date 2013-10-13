from django.contrib import admin
from camm.models import Simulation
from camm.models import SimulationRequest


class SimulationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
    ]
    

class SimulationRequestAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "computing_resource", "remote_login", "scratch_area", "experiment_data"]


admin.site.register(Simulation, SimulationAdmin)
admin.site.register(SimulationRequest, SimulationRequestAdmin)


