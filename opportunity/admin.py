from django.contrib import admin
from .models import Opportunity, ApplicationLink, VisitorCount

admin.site.register(Opportunity)
admin.site.register(ApplicationLink)
admin.site.register(VisitorCount)
