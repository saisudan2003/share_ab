from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.utils import IntegrityError
from django.contrib import messages
import pyautogui


# Create your views here.
def landing(request):
    return render(request,'users/landing.html')
def login_view(request):
    if request.method == "POST":
        usern = request.POST['username']
        passw = request.POST['password']
        user = authenticate(username=usern,password=passw)
        print(usern,passw)
        if user is not None:
            login(request,user)
            if request.user.is_authenticated:
                return redirect('home')
            else:
                messages.warning(request,"Please check your password")
                return render(request,'users/login.html')
        else:
            messages.warning(request,"Please check your password")
            return render(request,'users/login.html')

    return render(request,'users/login.html')
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        print(username,email,password1,password2)
        if password1 != password2:
            messages.warning(request,"Please check your password")
            return render(request,'users/signup.html')
        else:
            try:
                myuser = User.objects.create_user(username,email,password1)
                myuser.save()
                request.session['user_id'] = myuser.id

            except IntegrityError as e:
                messages.warning(request,"User already exists")
                return render(request,'users/signup.html')

            return redirect('createprofile')
    return render(request,'users/signUp.html')

def createprofile(request):
    if request.method == "POST":
        name = request.POST['name']
        age = request.POST['age']
        gender = request.POST['gender']
        phone = request.POST['phone'] 
        profile_picture = request.FILES['profile_picture']

        user_id = request.session.get('user_id')

        if user_id is None:
            messages.warning(request,"Failed to create profile")
            return redirect('login')


        person = Person(
            user_cred_id_id=user_id,
            name=name,
            age=age,
            gender=gender,
            phone=phone,
            profile_picture=profile_picture
        )
        person.save()
        del request.session['user_id']
        return redirect('home')
        
    return render(request, 'users/createprofile.html')

def home(request):
    requests = Request.objects.all()
    return render(request, 'users/homepage.html', {'requests': requests})

def addrequest(request):
    return HttpResponse("addrequest")

def myrequests(request):
    user_id = request.user.id
    requests = Request.objects.filter(request_owner=user_id)
    return render(request, 'users/myrequests.html', {'requests': requests})
    
#---------working---------
# def myrequests_single(request):
#     request_id = request.GET.get('request_id')
#     selected_request = get_object_or_404(Request, id=request_id)
#     messages = Message.objects.filter(request_id=selected_request)

#     return render(request, 'users/myrequests_single.html', {
#         'selected_request': selected_request,
#         'messages': messages,
#     })
#----------------------------

def myrequests_single(request):
    request_id = request.GET.get('request_id')
    selected_request = get_object_or_404(Request, id=request_id)

    messages = Message.objects.filter(request_id=selected_request)
    senders = [msg.sender for msg in messages]
    statuses = Requested_users_status.objects.filter(user__in=senders, request=selected_request, status=0)

    valid_sender_ids = set(user.id for status in statuses for user in status.user.all())

    newmessages = [msg for msg in messages if msg.sender.id in valid_sender_ids]

    return render(request, 'users/myrequests_single.html', {
        'selected_request': selected_request,
        'messages': newmessages,
    })


def accept_request(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        message = get_object_or_404(Message, id=message_id)
        request_instance = message.request_id

        # Perform logic to accept the request
        if request_instance.no_passengers > 0:
            # Deduct the number of passengers by 1
            request_instance.no_passengers -= 1
            request_instance.save()

            # Set status as 1 for the user and the request
            status = Requested_users_status.objects.get(user=message.sender, request=request_instance)
            status.status = 1
            status.save()
    return redirect('home')
    

def decline_request(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        message = get_object_or_404(Message, id=message_id)
        request_instance = message.request_id

        # Perform logic to decline the request
        # Set status as -1 for the user and the request
        status = Requested_users_status.objects.get(user=message.sender, request=request_instance)
        status.status = -1
        status.save()
    return redirect('home')
    

def sent_requests_status(request):
    return HttpResponse("sent_requests_status")

def profile(request):
    user_id = request.user.id
    person = Person.objects.get(user_cred_id=user_id)
    return render(request, 'users/profile.html', {'person': person})

def editprofile(request):
    return HttpResponse("edit profile")

def logout_view(request):
    return HttpResponse("logout")


