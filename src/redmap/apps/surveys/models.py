from django.db import models

class Survey(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    enabled = models.BooleanField(default=False)
    survey = models.TextField(blank=True)
