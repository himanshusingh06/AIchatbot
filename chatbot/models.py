from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'
    


class ContactMessage(models.Model):
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
    subject = models.CharField(max_length=255)
    user_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.user_name} ({self.user_email})'

# models.py


class ProUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    
def is_pro_user(self):
    return ProUser.objects.filter(user=self).exists()

User.add_to_class('is_pro_user', is_pro_user)