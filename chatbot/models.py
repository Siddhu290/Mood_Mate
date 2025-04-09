from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Additional user fields if needed

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class MoodAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

class FacialExpression(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    expression = models.CharField(max_length=20)  # e.g., happy, sad, angry, neutral
    confidence = models.FloatField()
    image_data = models.TextField(blank=True, null=True)  # Base64 encoded image data (optional)
    camera_enabled = models.BooleanField(default=True)  # Track if camera was enabled for this session

    def __str__(self):
        return f"{self.user.username} - {self.expression} ({self.timestamp})"
