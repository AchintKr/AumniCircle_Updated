from django.contrib import admin
from django.urls import path
from home import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index,name='index'),
    path('signup',views.signup,name='signup'),
    path('signin',views.signin,name='signin'),
    path('upload',views.upload,name='upload'),
    path('profile/<str:pk>',views.profile,name='profile'),
    path('forget-password',views.ForgetPassword,name='forget_password'),
    path('change-password/<token>/',views.ChangePassword,name='change_password'),
    #path('verify/<token>/',views.verify,name='verify'),
    path('confirm-donation/<uuid:donation_id>/', views.confirm_donation, name='confirm_donation'),
    path('like-post',views.like_post,name='like-post'),
    path('setting',views.setting,name='setting'),
    path('leaderboard',views.leaderboard,name="leaderboard"),
    path('search',views.search,name='search'),
    path('events', views.event, name='event'),
    path('feedback', views.feedback, name='feedback'),
    path('thank-you', views.thank_you, name='thank_you'),
    path('job_portal', views.job_portal, name='job_portal'),
    path('post-job/', views.post_job, name='post_job'),
    path('group/<int:group_id>/', views.group_chat, name='group_chat'),
    # path('send-message/<int:group_id>/', views.send_message, name='send_message'),
    path('verify-college/<int:profile_id>/', views.verify_college, name='verify_college'),
    path('donate',views.donate,name='donate'),
    path('add-comment/<uuid:post_id>/', views.add_comment, name='add_comment'),
    path('follow/<str:pk>',views.follow,name='follow'),
    path('logout',views.logout,name='logout'),
    path('leaderboard',views.leaderboard,name="leaderboard"),
    path('success_story',views.success_story,name='success_story'),
    path('verification-success', views.verification_success, name='verification_success'),
]
if settings.DEBUG:
   urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)