from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from .models import Opportunity
from .serializers import OpportunitySerializer, OpportunityCreateUpdateSerializer


# Custom paginator that returns 10 items per page
class OpportunityPagination(PageNumberPagination):
    page_size = 10
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
