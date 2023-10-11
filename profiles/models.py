from django.db import models
from accounts.models import Account

class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField( upload_to='profile_images/', blank=True)
    def __str__(self):
        return self.user.username


