from django.urls import path
from .views import OpportunityView, OpportunityDetailView

app_name = "opportunity"
urlpatterns = [
    path("", OpportunityView.as_view(), name="opportunity-list"),
    path(
        "<str:title_slug>/", OpportunityDetailView.as_view(), name="opportunity-detail"
    ),
]
