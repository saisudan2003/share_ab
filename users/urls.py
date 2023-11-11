from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('createprofile/', views.createprofile, name='createprofile'),
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('addrequests/', views.addrequests, name='addrequest'),
    path('myrequests/', views.myrequests, name='myrequests'),
    path('myrequests_single/', views.myrequests_single, name='myrequests_single'),
    path('sent_requests_status/', views.sent_requests_status, name='sent_requests_status'),
    path('profile/', views.profile, name='profile'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('logout/', views.logout_view, name='logout'),
    path('send_message/<int:request_id>/', views.send_message, name='send_message'),
    path('accept_request/', views.accept_request, name='accept_request'),
    path('decline_request/', views.decline_request, name='decline_request'),
    path('view_user_profile/', views.view_user_profile, name='view_user_profile'),
    path('edit_request/', views.edit_request, name='edit_request'),
]


    
