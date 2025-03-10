from rest_framework import serializers
from .models import ApplicationLink, Opportunity, HackathonOpportunity


class HackathonOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HackathonOpportunity
        fields = [
            "id",
            "application_link",
            "img",
            "title",
            "slug",
            "time_left",
            "location",
            "prize",
            "participants",
            "host",
            "date_range",
            "themes",
            "description",
        ]


class ApplicationLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationLink
        fields = ["url"]


class OpportunitySerializer(serializers.ModelSerializer):
    application_links = ApplicationLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "category",
            "date_posted",
            "link",
            "description",
            "og_image_url",
            "og_description",
            "slug",
            "application_links",
        ]


class OpportunityCreateUpdateSerializer(serializers.ModelSerializer):
    application_link_urls = serializers.ListField(
        child=serializers.URLField(), write_only=True, required=False
    )

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "category",
            "date_posted",
            "link",
            "description",
            "og_image_url",
            "og_description",
            "slug",
            "application_link_urls",
        ]

    def create(self, validated_data):
        # Extract application link URLs if provided
        application_link_urls = validated_data.pop("application_link_urls", [])

        # Create the opportunity
        opportunity = Opportunity.objects.create(**validated_data)

        # Create and add application links
        for url in application_link_urls:
            link, _ = ApplicationLink.objects.get_or_create(url=url)
            opportunity.application_links.add(link)

        return opportunity

    def update(self, instance, validated_data):
        # Extract application link URLs if provided
        application_link_urls = validated_data.pop("application_link_urls", None)

        # Update opportunity fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update application links if provided
        if application_link_urls is not None:
            # Clear existing links
            instance.application_links.clear()

            # Add new links
            for url in application_link_urls:
                link, _ = ApplicationLink.objects.get_or_create(url=url)
                instance.application_links.add(link)

        return instance
