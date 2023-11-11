from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.utils import IntegrityError
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string


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
    return render(request,'users/signup.html')

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
    return render(request, 'users/dashboard.html', {'requests': requests})

def addrequest(request):
    return HttpResponse("addrequest")

def myrequests(request):
    user_id = request.user.id
    requests = Request.objects.filter(request_owner=user_id)
    return render(request, 'users/myrequests_n.html', {'requests': requests})
    
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

    return render(request, 'users/myrequests_single_n.html', {
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
    return render(request, 'users/profile_n.html', {'person': person})

 # Import the form you need to create



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

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')  # Redirect to the same page or any other desired page after saving changes

    return render(request, 'users/editprofile.html', {'person': person})



def logout_view(request):
    return HttpResponse("logout")

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

        messages.success(request, 'Request added successfully!')
        return redirect('profile')  # Redirect to the same page or any other desired page after saving the request

    return render(request, 'users/addrequests.html')  # Replace 'your_template_name' with the actual template name




def reset_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        # Check if the email exists in the database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.warning(request, "Invalid email address. Please provide a valid email.")
            return render(request, 'users/resetpwd.html')

        # Generate a random password
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        # Set the new password for the user
        user.set_password(new_password)
        user.save()

        # Send an email with the new password
        send_mail(
            'Password Reset',
            f'Your new password is: {new_password}',
            settings.EMAIL_HOST_USER,  # Sender's email address
            [email],  # Recipient's email address
            fail_silently=False,
        )

        messages.success(request, "An email with the new password has been sent to your email address.")
        return redirect('login')  # Redirect to the login page

    return render(request, 'users/resetpwd.html')


from django.http import JsonResponse
from .models import Message

def send_message(request):
    if request.method == 'POST' and request.is_ajax():
        sender = request.user
        receiver_id = request.POST.get('receiver_id')
        request_id = request.POST.get('request_id')
        message_text = request.POST.get('message')

        # Create a new message
        message = Message.objects.create(
            sender=sender,
            receiver_id=receiver_id,
            request_id=request_id,
            message=message_text,
            message_date=timezone.now()  # You may need to import timezone
        )

        return JsonResponse({'status': 'success', 'message_id': message.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})