from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.utils import IntegrityError
from django.urls import path
import pyautogui

from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.utils import timezone
from django.db.models import Q

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

@login_required
def home(request):
    current_datetime = timezone.now()

    # Get all requests excluding the current user and filter by trip_date_time
    all_requests = Request.objects.exclude(request_owner=request.user).filter(
        trip_date_time__gte=current_datetime).order_by('trip_date_time')

    # Check if the user submitted a search request
    selected_date = request.GET.get('selected_date')
    if selected_date:
        # Filter requests based on the selected date
        selected_date_requests = all_requests.filter(
            trip_date_time__date=selected_date)
        return render(request, 'users/homepage.html', {'requests': selected_date_requests, 'selected_date': selected_date})

    # If no search is performed, display all requests
    return render(request, 'users/homepage.html', {'requests': all_requests})

# @login_required
# def send_message(request, request_id):
#     if request.method == 'POST':
#         message_text = request.POST.get('message')

#         # Get the selected request and create a new message
#         selected_request = get_object_or_404(Request, id=request_id)
#         message_new = Message.objects.create(
#             sender=request.user,
#             receiver=selected_request.request_owner,
#             request_id=selected_request,
#             message=message_text,
#             message_date=timezone.now(),
#         )
#         message_new.save()
#         # Add the user to the requested_users of the request
#         selected_request.requested_users.add(request.user)

#         # Update the Requested_users_status model initially with status 0
#         status, created = Requested_users_status.objects.get_or_create(
#             user=request.user,
#             request=selected_request,
#             defaults={'status': 0}
#         )

#         # Redirect to the 'home' view after successfully sending the message
#         return redirect('home')

#     return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def send_message(request, request_id):
    if request.method == 'POST':
        message_text = request.POST.get('message')  # Ensure 'message' is the correct name of your textarea input

        if message_text:
            # Get the selected request and create a new message
            selected_request = get_object_or_404(Request, id=request_id)
            message_new = Message.objects.create(
                sender=request.user,
                receiver=selected_request.request_owner,
                request_id=selected_request,
                message=message_text,
                message_date=timezone.now(),
            )
            message_new.save()
            
            # Add the user to the requested_users of the request
            selected_request.requested_users.add(request.user)

            # Update the Requested_users_status model initially with status 0
            # status, created = Requested_users_status.objects.get_or_create(
            #     user=request.user,
            #     request=selected_request,
            #     defaults={'status': 0}
            # )
            # status, created = Requested_users_status.objects.get_or_create(
            #     defaults={'status': 0}
            # )

            # # Adding the user and request to the many-to-many fields
            # status.user.add(request.user)
            # status.request.add(selected_request)

            status_query = Requested_users_status.objects.filter(
                user=request.user,
                request=selected_request
            )

            if status_query.exists():
                # If the instance exists, use the first one
                status = status_query.first()
            else:
                # If the instance doesn't exist, create a new one
                status = Requested_users_status.objects.create(
                    user=request.user,
                    request=selected_request,
                    status=0  # Set the default status here
                )

            # Redirect to the 'home' view after successfully sending the message
            return redirect('home')

    # Handle GET request
    return render(request, 'users/send_message.html', {'request_id': request_id})
def new_send_message(request,request_id):
    if request.method == 'POST':
        message_text = request.POST.get('message')  # Ensure 'message' is the correct name of your textarea input
        send_message()





# def send_message(request, request_id):
#     return render(request, 'users/send_message.html', {'request_id': request_id})

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

    # Query Requested_users_status for the selected_request
    statuses = Requested_users_status.objects.filter(request=selected_request, status=0)

    valid_sender_ids = set(status.user.id for status in statuses)

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
            status, created = Requested_users_status.objects.get_or_create(
                user=message.sender,
                request=request_instance,
                defaults={'status': 1}
            )
            if not created:
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
        status, created = Requested_users_status.objects.get_or_create(
            user=message.sender,
            request=request_instance,
            defaults={'status': -1}
        )
        if not created:
            status.status = -1
            status.save()
    return redirect('home')

    

@login_required
def sent_requests_status(request):
    user_id = request.user.id

    # Get all messages sent by the user
    sent_messages = Message.objects.filter(sender=request.user)

    # Get the most recent message date for each request
    latest_message_dates = sent_messages.values('request_id').annotate(latest_date=Max('message_date'))

    # Get the full information for each request, including the latest message and status
    request_data = []
    for date in latest_message_dates:
        sent_request = Request.objects.get(id=date['request_id'])
        latest_message = Message.objects.filter(request_id=sent_request).latest('message_date')
        status = Requested_users_status.objects.filter(request=sent_request, user=request.user).first()

        request_data.append({
            'request_owner': sent_request.request_owner,
            'trip_date_time': sent_request.trip_date_time,
            'latest_message': latest_message.message,
            'latest_message_date': latest_message.message_date,
            'status': status.status if status else None,
        })

    # Sort the request_data based on the latest_message_date in descending order
    sorted_request_data = sorted(request_data, key=lambda x: x['latest_message_date'], reverse=True)

    return render(request, 'users/my_sent_request.html', {'request_data': sorted_request_data})

def profile(request):
    user_id = request.user.id
    person = Person.objects.get(user_cred_id=user_id)
    return render(request, 'users/profile.html', {'person': person})

def editprofile(request):
    return HttpResponse("edit profile")

def view_user_profile(request):
    if request.method == 'POST':
        search_username = request.POST.get('search_username')
        if search_username:
            # Search for the user
            searched_user = get_object_or_404(User, username=search_username)

            # Get the details of the searched user
            person_details = Person.objects.get(user_cred_id=searched_user.id)

            return render(request, 'users/view_user_profile.html', {'person': person_details})
    
    return render(request, 'users/view_user_profile.html')

def logout_view(request):
    return HttpResponse("logout")



