from django.urls import path
from .views import (
    OpportunityView,
    OpportunityDetailView,
    SearchView,
    HackathonOpportunityView,
    HackathonOpportunityDetailView,
)

app_name = "opportunity"
urlpatterns = [
    path("", OpportunityView.as_view(), name="opportunity-list"),
    path(
        "<str:title_slug>/", OpportunityDetailView.as_view(), name="opportunity-detail"
    ),
    path("search", SearchView.as_view(), name="search"),
    path("hackathons", HackathonOpportunityView.as_view(), name="hackathons0list"),
    path(
        "hackathons/<str:title_slug>",
        HackathonOpportunityDetailView.as_view(),
        name="hackathon-detail",
    ),
]
