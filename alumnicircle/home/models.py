from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from django.utils import timezone
from .helpers import *

User = get_user_model()
# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    id_user = models.IntegerField(blank=True, null=True)  # Consider setting null=True and blank=True
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    group = models.CharField(max_length=100, blank=True, null=True) 
    collegepic = models.ImageField(default='soa.jpg',null=True)
    email = models.EmailField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank_profile.jpg', null=True)
    idimg = models.ImageField(upload_to='id_images', default='blank_profile.jpg', null=True)
    regid = models.CharField(max_length=100, blank=True,null=True)
    jobprofile = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    college = models.CharField(max_length=100, blank=True)
    link_url = models.URLField(null=True,blank=True)
    point =  models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.id_user:
            self.id_user = self.user.id  # Automatically set id_user to the User's ID
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    id = models.UUIDField(primary_key = True,default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user
    

    
class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)
    
    def __str__(self):
        return self.username

    
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user
    
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user} - {self.text[:20]}'
    
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    poster = models.ImageField(upload_to='event_posters/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(null=True,blank=True)

    def __str__(self):
        return self.created_by

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    salary = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# class Group(models.Model):
#     name = models.CharField(max_length=100)
#     members = models.ManyToManyField(User, related_name='custom_groups')
    
#     def __str__(self):
#         return self.name

# class Message(models.Model):
#     group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
#     sender = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f'{self.sender.username}: {self.content[:20]}'    

class Donation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    graduation_year = models.IntegerField()
    transaction_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.full_name} - {self.amount} INR"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        
class SuccessStory(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='success_stories/', default='blank_profile.jpg', null=True)

    def __str__(self):
        return self.title
        
class Feedback(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Current Student'),
        ('alumni', 'Alumni'),
    ]
    FEEDBACK_TYPE_CHOICES = [
        ('idea', 'Idea'),
        ('result', 'Result'),
        ('opinion', 'Opinion'),
        ('survey', 'Survey'),
        ('comment', 'Comment'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES
    )
    graduation_year = models.PositiveIntegerField()
    feedback_type = models.CharField(
        max_length=10,
        choices=FEEDBACK_TYPE_CHOICES
    )
    feedback_text = models.TextField()

    def __str__(self):
        return f'{self.name} - {self.feedback_type}'
    
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('donation', 'Donation'),
        ('verified','Verified'),
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    text = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    seen_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Notification from {self.sender} to {self.receiver}'
    
    class Meta:
        ordering = ['-created_at']
    


    