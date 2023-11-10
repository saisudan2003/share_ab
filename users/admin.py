from django.contrib import admin
from .models import Person, Request, Message, Requested_users_status

# Register your models here.
admin.site.register(Person)
admin.site.register(Request)
admin.site.register(Message)
admin.site.register(Requested_users_status)
