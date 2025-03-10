from django.db import models
from django.utils import timezone


class ApplicationLink(models.Model):
    url = models.URLField(max_length=500, verbose_name="Application Link")

    def __str__(self):
        return self.url

    class Meta:
        verbose_name_plural = "Application Links"


class Opportunity(models.Model):
    title = models.CharField(max_length=300, verbose_name="Opportunity Title")
    category = models.CharField(max_length=50, verbose_name="Opportunity Type")
    date_posted = models.DateField(default=timezone.now)
    link = models.URLField(max_length=500, verbose_name="Opportunity Link")
    description = models.TextField(verbose_name="Opportunity Description")
    application_links = models.ManyToManyField(
        ApplicationLink, related_name="opportunities", blank=True
    )
    og_image_url = models.CharField(max_length=200, blank=True, null=True)
    og_description = models.TextField(max_length=500, blank=True, null=True)
    slug = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.category}"

    class Meta:
        verbose_name_plural = "Opportunities"
        ordering = ["-date_posted"]


class VisitorCount(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"Visitor Count: {self.count}"


class HackathonOpportunity(models.Model):
    application_link = models.URLField(max_length=500)
    img = models.URLField(max_length=500, blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=200, blank=True, null=True)
    time_left = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    prize = models.CharField(max_length=100)
    participants = models.CharField(max_length=50)
    host = models.CharField(max_length=100)
    date_range = models.CharField(max_length=100)
    themes = models.JSONField()  # Storing the list of themes as JSON
    description = models.TextField()  # Long HTML content
    date_posted = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date_posted"]


# http://127.0.0.1:8000/api/v1/opportunities/?category=Internship
# postgresql://oppu_db_user:cJwRvXsiNcYrfyNknwwlOqIlwOKADoBN@dpg-cv4crmnnoe9s73c9nrdg-a/oppu_db
