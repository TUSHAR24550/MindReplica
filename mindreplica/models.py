from django.db import models
from django.contrib.auth.models import User

class Memory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text_input = models.TextField(blank=True, null=True)
    file_upload = models.FileField(upload_to="memories/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text_input[:50] if self.text_input else "Memory"
    
    
    # ✅ NEW — Chat History Model
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # jo baat kar raha hai
    twin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="twin_messages", null=True, blank=True)  # jis twin se baat ho rahi hai
    message = models.TextField()        # user ka message
    reply = models.TextField()          # AI ka reply
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.twin}: {self.message[:30]}"