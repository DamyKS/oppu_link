from django.contrib import admin
from .models import Opportunity, ApplicationLink, VisitorCount, HackathonOpportunity

admin.site.register(Opportunity)
admin.site.register(ApplicationLink)
admin.site.register(VisitorCount)
admin.site.register(HackathonOpportunity)
