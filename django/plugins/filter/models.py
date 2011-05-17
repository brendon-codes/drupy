from django.db import models

class FilterFormat(models.Model):
    name = models.CharField(max_length=255)


