from django.urls import path
from .views import OpportunityView

app_name = "opportunity"
urlpatterns = [
    path("", OpportunityView.as_view(), name="opportunity-list"),
]
