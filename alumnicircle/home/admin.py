from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Comment)
admin.site.register(Event)
admin.site.register(Job)
admin.site.register(Donation)
admin.site.register(SuccessStory)
admin.site.register(Feedback)
admin.site.register(Notification)

