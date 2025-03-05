from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Opportunity
from .serializers import OpportunitySerializer, OpportunityCreateUpdateSerializer


class OpportunityView(APIView):
    def get(self, request):
        """
        Retrieve all opportunities or filter based on query parameters
        """
        # Get query parameters
        category = request.query_params.get("category")

        # Base queryset
        opportunities = Opportunity.objects.all()

        # Optional filtering by category
        if category:
            opportunities = opportunities.filter(category=category)

        # Serialize the queryset
        serializer = OpportunitySerializer(opportunities, many=True)

        return Response(serializer.data)

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
