from django.db import models

class ApiCache(models.Model):
    request_hash = models.CharField(max_length=64, unique=True)
    response_data = models.TextField()  # Store JSON or string response
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.request_hash
