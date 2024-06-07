from django.db import models

class UserActivity(models.Model):
    user_id = models.CharField(max_length=100)
    activity_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    details = models.JSONField()
