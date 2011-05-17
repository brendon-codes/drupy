from django.db import models

class Plugin(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField()

