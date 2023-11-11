from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import *
from .models import Request
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
        return redirect('login')
        
    return render(request, 'users/createprofile.html')

# @login_required
# def home(request):
#     current_datetime = timezone.now()

#     all_requests = Request.objects.exclude(request_owner=request.user).filter(
#         trip_date_time__gte=current_datetime).order_by('trip_date_time')

#     selected_date = request.GET.get('selected_date')
#     if selected_date:
#         selected_date_requests = all_requests.filter(
#             trip_date_time__date=selected_date)
#         return render(request, 'users/homepage.html', {'requests': selected_date_requests, 'selected_date': selected_date})

#     if request.method == 'POST':
#         reqid = request.POST.get('request_id')
#         send_message(request, reqid)
#     return render(request, 'users/homepage.html', {'requests': all_requests})

@login_required
def home(request):
    current_datetime = timezone.now()
    all_requests = Request.objects.exclude(request_owner=request.user).filter(
        trip_date_time__gte=current_datetime).order_by('trip_date_time')

    user_requests_status = Requested_users_status.objects.filter(
        user=request.user)

    excluded_request_ids = [status.request.id for status in user_requests_status]

    all_requests = all_requests.exclude(id__in=excluded_request_ids)

    selected_date = request.GET.get('selected_date')
    if selected_date:
        selected_date_requests = all_requests.filter(
            trip_date_time__date=selected_date)
        return render(request, 'users/homepage.html', {'requests': selected_date_requests, 'selected_date': selected_date})

    if request.method == 'POST':
        reqid = request.POST.get('request_id')
        send_message(request, reqid)

    return render(request, 'users/homepage.html', {'requests': all_requests})


# def home(request):
#     current_datetime = timezone.now()
#     # Exclude requests from the current user and filter by trip_date_time
#     requests = Request.objects.exclude(request_owner=request.user) \
#                               .filter(trip_date_time__gte=current_datetime) \
#                               .order_by('trip_date_time')  # Order by trip_date_time in ascending order

#     reqid = request.POST.get('request_id')
#     send_message(request, reqid)
#     return render(request, 'users/homepage.html', {'requests': requests})



@login_required
def send_message(request, request_id):
    if request.method == 'POST':
        message_text = request.POST.get('message') 

        if message_text:
            selected_request = get_object_or_404(Request, id=request_id)
            message_new = Message.objects.create(
                sender=request.user,
                receiver=selected_request.request_owner,
                request_id=selected_request,
                message=message_text,
                message_date=timezone.now(),
            )
            print(message_new)
            message_new.save()
            
            selected_request.requested_users.add(request.user)

            status_query = Requested_users_status.objects.filter(
                user=request.user,
                request=selected_request
            )

            if status_query.exists():
                status = status_query.first()
            else:
                status = Requested_users_status.objects.create(
                    user=request.user,
                    request=selected_request,
                    status=0 
                )
            return redirect('home')

    # Handle GET request
    return render(request, 'users/send_message.html', {'request_id': request_id})





# def send_message(request, request_id):
#     return render(request, 'users/send_message.html', {'request_id': request_id})

def addrequests(request):
    
    if request.method == 'POST':
        # Get data from the form
        trip_date_time = request.POST['trip_date_time']
        desc = request.POST['desc']
        no_passengers = request.POST['no_passengers']

        # Assuming request_owner should be the currently logged-in user
        request_owner = request.user

        # Create a new Request object
        new_request = Request(
            request_create_date=timezone.now(),
            trip_date_time=trip_date_time,
            desc=desc,
            no_passengers=no_passengers,
            request_owner=request_owner,
        )

        new_request.save()

        return redirect('myrequests')  # Redirect to the same page or any other desired page after saving the request

    return render(request, 'users/addrequests.html')  # Replace 'your_template_name' with the actual template name

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
    user_id = request.user.id
    person = Person.objects.get(user_cred_id=user_id)

    if request.method == 'POST':
        # Handle form submission
        person.name = request.POST['name']
        person.age = request.POST['age']
        person.gender = request.POST['gender']
        person.phone = request.POST['phone']

        # Handle the profile picture
        if 'profile_picture' in request.FILES:
            person.profile_picture = request.FILES['profile_picture']

        person.save()

        # messages.success(request, 'Profile updated successfully!')
        return redirect('profile')  # Redirect to the same page or any other desired page after saving changes

    return render(request, 'users/editprofile.html', {'person': person})

def edit_request(request):
    request_id = request.GET.get('request_id')
    existing_request = get_object_or_404(Request, id=request_id)

    # Assuming you have some permission logic
    if not request.user.is_authenticated or request.user != existing_request.request_owner:
        return render(request, 'error_page.html', {'error_message': 'You do not have permission to edit this request.'})

    if request.method == 'POST':
        existing_request.trip_date_time = request.POST['trip_date_time']
        existing_request.desc = request.POST['desc']
        existing_request.no_passengers = request.POST['no_passengers']

        existing_request.save()

        return redirect('profile')  # Redirect to the same page or any other desired page after saving changes

    return render(request, 'users/edit_request.html', {'existing_data': existing_request})

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



