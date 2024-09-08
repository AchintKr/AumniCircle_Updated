from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User,auth,Group
from .models import *
from django.contrib.auth.decorators import login_required,user_passes_test
from itertools import chain
from django.views.decorators.csrf import csrf_exempt
import  random
import datetime 
import uuid
from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings
from .helpers import *

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    try:
        user_profile = Profile.objects.get(user=user_object)
    except Profile.DoesNotExist:
        # Handle the case where the profile does not exist
        user_profile = None  # or you can redirect to a profile creation page
    user_following_list = []
    feed=[]
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)
        
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)
    
    feed_lists = list(chain(*feed))
    posts = Post.objects.all()
    # user suggestion starts 
    current_notification=[]
    current_notification = Notification.objects.filter(receiver = request.user).order_by("-created_at")
    all_users = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
        
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)
    
    username_profile=[]
    username_profile_list = []
    
    for users in final_suggestions_list:
        username_profile.append(users.id)
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)
        
    suggestions_username_profile_list = list(chain(*username_profile_list))
    
    return render(request, 'index.html', {'user_profile': user_profile,'notifications':current_notification ,'posts': feed_lists,'suggestions_username_profile_list':suggestions_username_profile_list[:4]})

def leaderboard(request):
    leaderboard = Profile.objects.all().order_by("-point")
    return render(request,"leaderboard.html",{'leaderboard':leaderboard})
def confirm_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    send_certificate(donation)
    Notification.objects.create(
            sender=request.user,
            receiver=request.user,
            notification_type='donate',
            text=f'Thank you for Your Donation .',
            url=f'/donate')
    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)
    user_profile.point += int(donation.amount)
    user_profile.save()
    return render(request,'success-don.html',{'doantion':donation}) 

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)
        username_profile = []
        username_profile_list = []
        for users in username_object:
            username_profile.append(users.id)
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request,'search.html',{'user_profile':user_profile,'username_profile_list':username_profile_list})    

@login_required(login_url='signin')
def setting(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        work = request.POST.get('work')
        link_url = request.POST.get('link_url')

        pimage = request.FILES.get('pimage')
        if pimage:
            user_profile.profileimg = pimage

        cimage = request.FILES.get('cimage')
        if cimage:
            user_profile.idimg = cimage
            user_profile.save()  # Save before sending email to get profile ID
            send_verification_email(user_profile)
            
            

        user_profile.bio = bio
        user_profile.location = location
        user_profile.jobprofile = work
        user_profile.link_url=link_url

        user_profile.id_user = request.user.id  # Set id_user to the user's ID
        user_profile.save()
        
        return redirect('setting')

    return render(request, 'setting.html', {'user_profile': user_profile})

    
@login_required(login_url='signin')
def upload(request):
   if request.method == 'POST':
       user = request.user.username
       image = request.FILES.get('image_upload')
       caption = request.POST['caption']
       user_object = User.objects.get(username=user)
       user_profile = Profile.objects.get(user=user_object)
       user_profile.point += 100
       user_profile.save()
       new_post = Post.objects.create(user=user,image=image,caption=caption)
       new_post.save()
       return redirect('/')
   else:
       return redirect('/')
@login_required(login_url='signin')
def like_post(request): 
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    user_object = User.objects.get(username=post.user)
    profile = Profile.objects.get(user = user_object)
    like_filter = LikePost.objects.filter(post_id=post_id,username=username).first()
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id,username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        Notification.objects.create(
            sender=request.user,
            receiver=User.objects.get(username=post.user),
            notification_type='like',
            text=f' liked your post .',
            url=f'/profile/{request.user}')
        profile.point += 10
        profile.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        profile.point -= 10
        profile.save()
        return redirect('/')

@login_required(login_url='signin')
def event(request):
    if request.method == "POST":
        title = request.POST.get('title')
        date = request.POST.get('date')
        time = request.POST.get('time')
        url = request.POST.get('url')
        location = request.POST.get('location')
        description = request.POST.get('description')
        poster = request.FILES.get('poster')
        
        Event.objects.create(
            title=title,
            date=date,
            time=time,
            location=location,
            description=description,
            poster=poster,
            url=url,
            created_by=request.user,
            created_at=timezone.now()
            
        )
        return redirect('event')

    events = Event.objects.all().order_by('-date', '-time')
    profile_v = Profile.objects.get(user=request.user)
    str='event_non.html'
    if profile_v.is_verified:
        str = 'event.html'
    return render(request,str, {'events': events})
    
@login_required(login_url='signin')
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        comment = Comment.objects.create(post=post, user=request.user.username, text=text)
        comment.save()
        user_object = User.objects.get(username=post.user)
        profile = Profile.objects.get(user = user_object)
        profile.point += 20
        profile.save()
        Notification.objects.create(
            sender=request.user,
            receiver=User.objects.get(username=post.user),
            notification_type='comment',
            text=f' commented on your post .',
            url=f'/profile/{request.user}')
        return redirect('/')
    else:
        return redirect('/')
    
    
@login_required(login_url='signin')
def profile(request,pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)
    follower = request.user.username
    user = pk
    if FollowersCount.objects.filter(follower=follower,user=user).first():
        button_text = 'Unfollow'
    else:
        button_text='Follow'
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts':user_posts,
        'user_post_length':user_post_length,
        'button_text':button_text,
        'user_followers':user_followers,
        'user_following':user_following,
    }
    return render(request,'profile.html',context)

@login_required(login_url='signin')
def follow(request,pk):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        user_object = User.objects.get(username=pk)
        user_profile = Profile.objects.get(user=user_object)
        if FollowersCount.objects.filter(follower=follower,user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            user_profile.point -= 10
            user_profile.save()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower,user=user)
            new_follower.save()
            user_profile.point += 10
            Notification.objects.create(
            sender=request.user,
            receiver=user_profile.user,
            notification_type='follow',
            text=f' started following you',
            url=f'/profile/{request.user}')
            user_profile.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')

def success_story(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        title = request.POST.get('title')
        story_text = request.POST.get('story')
        image = request.FILES.get('image')

        # Fetch the user based on the username
        try:
            author = User.objects.get(username=username)
        except User.DoesNotExist:
            # Redirect to the same page with an error message
            return render(request, 'success_stories.html', {'error': 'User not found'})

        # Create and save the SuccessStory
        story = SuccessStory(author=author, title=title, description=story_text, image=image)
        story.save()
        user_profile=Profile.objects.get(user = request.user)
        user_profile.point+=50
        user_profile.save()
        # Fetch the latest stories
        latest_stories = SuccessStory.objects.all().order_by('-created_at')[:5]
        
        # Re-render the page with success message and updated stories
        return render(request, 'success_stories.html', {'latest_stories': latest_stories, 'success': 'Story added successfully!'})

    else:
        # For GET requests, just render the page with latest stories
        latest_stories = SuccessStory.objects.all().order_by('-created_at')[:5]
        return render(request, 'success_stories.html', {'latest_stories': latest_stories})
    
def feedback(request):
    if request.method == 'POST':
        # Extract data from the POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        user_type = request.POST.get('userType')
        graduation_year = request.POST.get('graduationYear')
        feedback_type = request.POST.get('feedbackType')
        feedback_text = request.POST.get('feedbackText')
        
        feedback = Feedback(
            name=name,
            email=email,
            user_type=user_type,
            graduation_year=int(graduation_year),
            feedback_type=feedback_type,
            feedback_text=feedback_text
        )

        # Save the Feedback instance to the database
        feedback.save()
        send_feedback(feedback)

        # Redirect to a thank you page
        return redirect('thank_you')
    
    return render(request, 'feedback.html')

def thank_you(request):
    return render(request, 'thank_you.html')    
    
    
def donate(request):
    if request.method == 'POST':
        donation_type = request.POST.get('donationType')
        amount = request.POST.get('amount')
        full_name = request.POST.get('full')
        email = request.POST.get('email')
        phone = request.POST.get('ph')
        graduation_year = request.POST.get('gyear')
        transaction_id = request.POST.get('tid')
        
        donation = Donation.objects.create(
            donation_type=donation_type,
            amount=amount,
            full_name=full_name,
            email=email,
            phone=phone,
            graduation_year=graduation_year,
            transaction_id=transaction_id
        )
        
        send_reconfirmation_email(donation)
        return redirect('donate')  # Redirect to the same page after submission
    
    latest_donations = Donation.objects.order_by('-created_at')[:5] 
    return render(request, 'donate.html', {'latest_donations': latest_donations})
    
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        password_confirm = request.POST.get('pass1')
        college = request.POST.get('uni')
        reg = request.POST.get('reg')

        # Check if passwords match
        if password != password_confirm:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
        
        if len(password)<8:
            messages.info(request, 'Password is Too Small should be greater than 7')
            return redirect('signup')

            
        
        # Check if email is already taken
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email is already taken')
            return redirect('signup')

        # Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username is already taken')
            return redirect('signup')

        # Validate 'reg' input
        if not reg.isdigit():
            messages.info(request, 'Registration ID must be a valid integer')
            return redirect('signup')

        reg_int = int(reg)
        if not (1000000000 <= reg_int <= 2999999999):
            messages.info(request, 'Registration ID is out of the valid range')
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Authenticate and log in the user
        user_login = auth.authenticate(username=username, password=password)
        if user_login is not None:
            auth.login(request, user_login)
        else:
            messages.info(request, 'Authentication failed')
            return redirect('signup')

        # Create the Profile with all required fields
        try:
            new_profile = Profile.objects.create(
                user=user,
                email=email,
                id_user=user.id,
                regid=reg_int,
                college=college,
                jobprofile='',
                location='',
                bio='',
                point=5,
            )
            new_profile.save()
        except Exception as e:
            messages.info(request, f'Error creating profile: {e}')
            return redirect('signup')

        return redirect('setting')

    else:
        return render(request, 'signup.html')
    
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        p = request.POST['pass']
        user = auth.authenticate(username=username,password=p)
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,"Inavlid Credentials")
            return redirect('signin')
    else:
        return render(request,'signin.html')
# Create your views here.
def ChangePassword(request, token):
    context = {}
    try:
        profile_obj = Profile.objects.filter(forget_password_token=token).first()

        if profile_obj is None:
            messages.error(request, 'Invalid or expired token.')
            return redirect('forget-password')  # Redirect to forget password page or any relevant page

        context = {'user_id': profile_obj.user.id}

        if request.method == 'POST':
            new_password = request.POST.get('pass')
            confirm_password = request.POST.get('pass1')
            user_id = request.POST.get('user_id')

            if user_id is None:
                messages.warning(request, 'No user ID found.')
                return redirect(f'/change-password/{token}/')

            if new_password != confirm_password:
                messages.warning(request, 'Passwords do not match.')
                return redirect(f'/change-password/{token}/')

            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.save()

            # Clear the token after successful password reset
            profile_obj.forget_password_token = None
            profile_obj.save()

            messages.success(request, 'Password changed successfully. Please sign in.')
            return redirect('signin')

    except Exception as e:
        print(e)
        messages.error(request, 'Something went wrong. Please try again.')
        return redirect('forget-password')  # Redirect to forget password page or any relevant page

    return render(request, 'change-password.html', context)

@login_required(login_url='signin')
def job_portal(request):
    query = request.GET.get('q')
    location = request.GET.get('location')
    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(company__icontains=query)
    if location:
        jobs = jobs.filter(location__icontains=location)

    return render(request, 'job_portal.html', {'jobs': jobs})

@login_required(login_url='signin')
def post_job(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company')
        location = request.POST.get('location')
        salary = request.POST.get('salary')
        description = request.POST.get('description')
        
        Job.objects.create(
            title=title,
            company=company,
            location=location,
            salary=salary,
            description=description
        )
        user_object = User.objects.get(username=request.user)
        user_profile = Profile.objects.get(user=user_object)
        user_profile.point += 120
        user_profile.save()
        return redirect('job_portal')  # Redirect back to job portal after posting
    return render(request, 'job_portal.html')


def ForgetPassword(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')

            if not User.objects.filter(username=username).exists():
                messages.warning(request, 'No user found with this username.')
                return redirect('/forget-password')

            user_obj = User.objects.get(username=username)
            token = str(uuid.uuid4())

            profile_obj, created = Profile.objects.get_or_create(user=user_obj)
            profile_obj.forget_password_token = token
            profile_obj.save()

            send_forget_password_mail(user_obj.email, token)
            messages.success(request, 'A link has been sent to your registered email.')
            return redirect('/forget-password')

    except Exception as e:
        print(e)
        messages.error(request, 'Something went wrong. Please try again.')
    
    return render(request, 'forget-password.html')

def verification_success(request):
    user_object = User.objects.get(username=request.user)
    profile = Profile.objects.get(user=user_object)
    profile.point += 200
    profile.save()
    Notification.objects.create(
            sender=request.user,
            receiver=request.user,
            notification_type='verified',
            text=f' Your Account has been verified Successfully .',
            url=f'/profile/{request.user}')
    return render(request, 'verification_success.html')


def verify_college(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    # group_name = profile.college
    # group, created = Group.objects.get_or_create(name=group_name)
        
    #     # Assign the user to the group
    # user = profile.user
    # user.groups.add(group)
        
    # Update the profile to indicate that the college is verified
    profile.is_verified = True
    profile.save()
        # Unlock additional features for the user
    messages.success(request, 'College ID verified successfully.')
    return redirect('verification_success')  # Redirect to a success page or any relevant page




def group_chat(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    messages = group.messages.order_by('timestamp')
    return render(request, 'group.html', {'group': group, 'messages': messages})

# @csrf_exempt
# def send_message(request, group_id):
#     if request.method == 'POST':
#         group = get_object_or_404(Group, id=group_id)
#         sender = request.user
#         content = request.POST.get('message')
        
#         if content:
#             Message.objects.create(group=group, sender=sender, content=content)
#             return JsonResponse({'status': 'success'})
        
#     return JsonResponse({'status': 'failed'})


# @login_required(login_url='signin')
# def some_view(request):
#     user_profile = Profile.objects.get(user=request.user)
#     if user_profile.is_verified:
#         # Show advanced features
#         pass
#     else:
#         # Show default features
#         pass
#     return render(request, 'some_template.html', {'user_profile': user_profile})

# def is_verified(user):
#     return user.profile.is_verified

# @login_required(login_url='signin')
# @user_passes_test(is_verified, login_url='default_features')
# def advanced_features(request):
#     # Only accessible to verified users
#     return render(request, 'advanced_features.html')

def logout(request):
    auth.logout(request)
    return redirect('signin')
