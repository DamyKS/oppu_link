from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from .models import Opportunity, VisitorCount
from .serializers import OpportunitySerializer, OpportunityCreateUpdateSerializer
from django.shortcuts import get_object_or_404


from .models import HackathonOpportunity
from .serializers import (
    HackathonOpportunitySerializer,
)


# Custom paginator that returns 10 items per page
class OpportunityPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"  # optional: allow client to set page size
    max_page_size = 160  # optional: maximum page size allowed


class OpportunityView(APIView):
    def get(self, request):
        """
        Retrieve all opportunities or filter based on query parameters with pagination.
        """
        # Get query parameters
        category = request.query_params.get("category")

        # Base queryset
        opportunities = Opportunity.objects.all()

        # Optional filtering by category
        if category:
            opportunities = opportunities.filter(category=category)

        # Instantiate paginator and paginate the queryset
        paginator = OpportunityPagination()
        paginated_opportunities = paginator.paginate_queryset(opportunities, request)

        # Serialize the paginated queryset
        serializer = OpportunitySerializer(paginated_opportunities, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a new opportunity
        """
        # Use the create/update serializer for writing
        serializer = OpportunityCreateUpdateSerializer(data=request.data)

        # Validate the input data
        if serializer.is_valid():
            # Save the opportunity
            opportunity = serializer.save()

            # Return the created opportunity using the read serializer
            response_serializer = OpportunitySerializer(opportunity)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        # If validation fails, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OpportunityDetailView(APIView):
    """
    Retrieve a single opportunity by its slug"""

    def get(self, request, title_slug):
        # get opportunity with slug = title_slug
        opportunity = get_object_or_404(Opportunity, slug=title_slug)
        serializer = OpportunitySerializer(opportunity)
        return Response(serializer.data)


# Custom paginator that returns 10 items per page
class HackathonOpportunityPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"  # allow client to override, e.g., ?page_size=20
    max_page_size = 160  # maximum page size allowed


class HackathonOpportunityView(APIView):
    def get(self, request):
        """
        Retrieve all hackathon opportunities
        """
        # theme = request.query_params.get("theme")
        opportunities = HackathonOpportunity.objects.all()

        paginator = HackathonOpportunityPagination()
        paginated_opportunities = paginator.paginate_queryset(opportunities, request)
        serializer = HackathonOpportunitySerializer(paginated_opportunities, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a new hackathon opportunity.
        """
        serializer = HackathonOpportunitySerializer(data=request.data)
        if serializer.is_valid():
            opportunity = serializer.save()
            response_serializer = HackathonOpportunitySerializer(opportunity)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HackathonOpportunityDetailView(APIView):
    """
    Retrieve a single hackathon opportunity by its slug.
    Note: The HackathonOpporyunity model must have a 'slug' field for this view to work.
    """

    def get(self, request, title_slug):
        opportunity = get_object_or_404(HackathonOpportunity, slug=title_slug)
        serializer = HackathonOpportunitySerializer(opportunity)
        return Response(serializer.data)


class VisitorCountView(APIView):
    def post(self, request):
        """
        Increment the visitor count
        """
        # Get the visitor count object
        visitor_count = get_object_or_404(VisitorCount, pk=1)

        # Increment the count
        visitor_count.count += 1
        visitor_count.save()

        return Response({"count": visitor_count.count})


class SearchView(APIView):
    """
    Search for opportunities using the search term provided in the request data.
    """

    def post(self, request):
        # for GET requests. Adjust accordingly if needed.
        search_term = request.data.get("search_term")
        opportunities = Opportunity.objects.filter(title__icontains=search_term)

        # Instantiate the paginator and paginate the queryset
        paginator = OpportunityPagination()
        paginated_opportunities = paginator.paginate_queryset(opportunities, request)

        # Serialize the paginated queryset
        serializer = OpportunitySerializer(paginated_opportunities, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)
